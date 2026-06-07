import json
import server
import client
from Crypto.Random import get_random_bytes

def create_vault():
    username = input("Username: ").strip()
    password = input("Master Password: ").strip()

    if not username or not password:
        print("Invalid input")
        return

    if server.get_vault(username):
        print("Username already exists. Use login instead.")
        return

    if not server.SERVER_ACTIVE:
        print("Server offline. Cannot create vault.")
        return

    master_key = get_random_bytes(16)

    local_share, server_share, recovery_share = client.split_secret(master_key)

    salt = get_random_bytes(16)
    kdf_key = client.derive_key(password, salt)

    enc_local, nonce_local = client.encrypt(
        json.dumps(local_share).encode(),
        kdf_key
    )

    vault = []

    enc_vault, nonce_vault = client.encrypt(
        json.dumps(vault).encode(),
        master_key
    )

    server.save_vault(
        username,
        json.dumps(server_share),
        enc_vault,
        nonce_vault
    )

    client.save_local(
        username,
        enc_local,
        nonce_local,
        salt,
        enc_vault,
        nonce_vault
    )

    print("\nVAULT CREATED SUCCESSFULLY")
    print("RECOVERY SHARE (SAVE THIS ONCE):")
    print(json.dumps(recovery_share))

def view_passwords(vault):
    print("\n--- YOUR VAULT ---")
    for i, item in enumerate(vault):
        cat = item.get("catatan", "")
        extra = f" | Catatan: {cat}" if cat else ""
        print(f"[{i}] {item['nama_layanan']} | {item['username']} | {item['password']}{extra}")

def add_password(vault, key, username, server_share, local):
    layanan = input("Service: ").strip()
    user = input("Username: ").strip()

    print("1. Manual Password")
    print("2. Auto Generate")
    opt = input("Choice: ")

    if opt == "1":
        pw = input("Password: ").strip()
    else:
        length = int(input("Length: "))
        pw = client.generate_password(length)

    catatan = input("Catatan: ").strip()

    vault.append({
        "nama_layanan": layanan,
        "username": user,
        "password": pw,
        "catatan": catatan
    })

    enc, nonce = client.encrypt(json.dumps(vault).encode(), key)
    server.save_vault(username, json.dumps(server_share), enc, nonce)
    client.save_local(
        username,
        local["enc_share"],
        local["nonce"],
        local["salt"],
        enc,
        nonce
    )

    print("ADDED")

def update_password(vault, key, username, server_share, local):
    view_passwords(vault)
    idx = input("Index (empty to cancel): ").strip()

    if idx == "":
        print("Cancelled")
        return

    if not idx.isdigit():
        print("Invalid input. Must be a number")
        return

    i = int(idx)

    if i < 0 or i >= len(vault):
        print("Invalid index")
        return

    new_user = input("New username: ").strip()
    new_pw = input("New password: ").strip()
    new_cat = input("New catatan: ").strip()

    if new_user:
        vault[i]["username"] = new_user
    if new_pw:
        vault[i]["password"] = new_pw
    if new_cat:
        vault[i]["catatan"] = new_cat

    enc, nonce = client.encrypt(json.dumps(vault).encode(), key)
    server.save_vault(username, json.dumps(server_share), enc, nonce)
    client.save_local(
        username,
        local["enc_share"],
        local["nonce"],
        local["salt"],
        enc,
        nonce
    )

    print("UPDATED")

def delete_password(vault, key, username, server_share, local):
    view_passwords(vault)
    idx = input("Index (empty to cancel): ").strip()

    if idx == "":
        print("Cancelled")
        return

    if not idx.isdigit():
        print("Invalid input. Must be a number")
        return

    i = int(idx)

    if i < 0 or i >= len(vault):
        print("Invalid index")
        return
    vault.pop(i)

    enc, nonce = client.encrypt(json.dumps(vault).encode(), key)
    server.save_vault(username, json.dumps(server_share), enc, nonce)
    client.save_local(
        username,
        local["enc_share"],
        local["nonce"],
        local["salt"],
        enc,
        nonce
    )

    print("DELETED")

def toggle_server():
    server.SERVER_ACTIVE = not server.SERVER_ACTIVE
    print("SERVER ACTIVE:", server.SERVER_ACTIVE)

def normal_mode():
    if not server.SERVER_ACTIVE:
        print("Server offline → switching to backup mode")
        backup_mode()

    username = input("Username: ")
    password = input("Master Password: ")

    srv = server.get_vault(username)
    if not srv:
        print("User not found")
        return

    local = client.load_local(username)
    if not local:
        print("Local data missing")
        return

    try:
        kdf_key = client.derive_key(password, local["salt"])

        local_share = json.loads(
            client.decrypt(local["enc_share"], kdf_key, local["nonce"])
        )

    except:
        print("AUTH FAILED")
        return

    try:
        server_share = json.loads(srv["server_share"])

        master_key = client.reconstruct_secret(local_share, server_share)

        vault = json.loads(
            client.decrypt(srv["vault_blob"], master_key, srv["nonce"])
        )
    except Exception as e:
        print("DECRYPT ERROR:", e)
        return

    while True:
        print("\n1. View")
        print("2. Add")
        print("3. Update")
        print("4. Delete")
        print("5. Exit")

        ch = input("> ")

        if ch == "1":
            view_passwords(vault)
        elif ch == "2":
            add_password(vault, master_key, username, server_share, local)
        elif ch == "3":
            update_password(vault, master_key, username, server_share, local)
        elif ch == "4":
            delete_password(vault, master_key, username, server_share, local)
        elif ch == "5":
            break

def backup_mode():
    username = input("Username: ")
    password = input("Master Password: ")
    recovery = input("Recovery Share: ")

    local = client.load_local(username)
    if not local:
        print("No local backup")
        return

    try:
        kdf_key = client.derive_key(password, local["salt"])

        local_share = json.loads(
            client.decrypt(local["enc_share"], kdf_key, local["nonce"])
        )

        recovery_share = json.loads(recovery)
        master_key = client.reconstruct_secret(local_share, recovery_share)
        vault = json.loads(
            client.decrypt(local["backup_vault"], master_key, local["backup_nonce"])
        )
        view_passwords(vault)

    except:
        print("BACKUP FAILED")

def main():
    server.init_db()

    while True:
        print("\n1. Create Vault")
        print("2. Login")
        print("3. Backup Mode")
        print("4. Exit")
        print("5. Toggle Server")

        ch = input("> ")

        if ch == "1":
            create_vault()

        elif ch == "2":
            normal_mode()

        elif ch == "3":
            backup_mode()

        elif ch == "4":
            break

        elif ch == "5":
            toggle_server()


if __name__ == "__main__":
    main()