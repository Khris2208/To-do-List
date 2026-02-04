"""
Program Jadwal Mingguan (CLI) - Bahasa Indonesia
Fitur:
- Tambah, edit, hapus (soft-delete), lihat, pulihkan kegiatan
- Field: hari, nomor (id), jam, kegiatan, status (sudah selesai/ belum)
- Data disimpan di file JSON (data.json dan trash.json)

Penggunaan: jalankan `python schedule.py` dan ikuti menu
"""
import json
import os
from datetime import datetime

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "data.json")
TRASH_FILE = os.path.join(DATA_DIR, "trash.json")
VALID_DAYS = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]


def ensure_data_dir():
    if not os.path.isdir(DATA_DIR):
        os.makedirs(DATA_DIR)


def load_json(path):
    if not os.path.exists(path):
        return {"next_id": 1, "items": []}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_state():
    ensure_data_dir()
    data = load_json(DATA_FILE)
    trash = load_json(TRASH_FILE)
    return data, trash


def save_state(data, trash):
    ensure_data_dir()
    save_json(DATA_FILE, data)
    save_json(TRASH_FILE, trash)


def print_item(item):
    status = "Selesai" if item.get("done") else "Belum"
    print(f"[{item['id']}] {item['hari']} {item['jam']} - {item['kegiatan']} (Status: {status})")


def list_all(data):
    if not data["items"]:
        print("Tidak ada kegiatan yang tersimpan.")
        return
    items = sorted(data["items"], key=lambda x: (VALID_DAYS.index(x["hari"]) if x["hari"] in VALID_DAYS else 7, x["jam"]))
    for item in items:
        print_item(item)


def list_by_day(data, hari):
    hari = hari.capitalize()
    if hari not in VALID_DAYS:
        print("Nama hari tidak valid. Gunakan: ", ", ".join(VALID_DAYS))
        return
    items = [i for i in data["items"] if i["hari"] == hari]
    if not items:
        print(f"Tidak ada kegiatan untuk hari {hari}.")
        return
    items = sorted(items, key=lambda x: x["jam"])
    for item in items:
        print_item(item)


def add_activity(data):
    hari = input("Hari (Senin/Minggu): ").strip().capitalize()
    if hari not in VALID_DAYS:
        print("Hari tidak valid.")
        return
    jam = input("Jam (format HH:MM): ").strip()
    # simple validation
    try:
        datetime.strptime(jam, "%H:%M")
    except Exception:
        print("Format jam salah. Gunakan HH:MM (24 jam).")
        return
    kegiatan = input("Nama kegiatan: ").strip()
    if not kegiatan:
        print("Kegiatan tidak boleh kosong.")
        return
    item = {
        "id": data["next_id"],
        "hari": hari,
        "jam": jam,
        "kegiatan": kegiatan,
        "done": False,
        "created_at": datetime.now().isoformat()
    }
    data["items"].append(item)
    data["next_id"] += 1
    print("Berhasil menambahkan kegiatan:")
    print_item(item)


def find_item(data, id_):
    for it in data["items"]:
        if it["id"] == id_:
            return it
    return None


def edit_activity(data):
    try:
        id_ = int(input("Masukkan nomor (id) kegiatan yang ingin diedit: "))
    except ValueError:
        print("Id harus berupa angka.")
        return
    it = find_item(data, id_)
    if not it:
        print("Kegiatan tidak ditemukan.")
        return
    print("Isi yang kosong untuk mempertahankan nilai lama.")
    hari = input(f"Hari [{it['hari']}]: ").strip().capitalize()
    if hari:
        if hari not in VALID_DAYS:
            print("Nama hari tidak valid.")
            return
        it["hari"] = hari
    jam = input(f"Jam [{it['jam']}]: ").strip()
    if jam:
        try:
            datetime.strptime(jam, "%H:%M")
            it["jam"] = jam
        except Exception:
            print("Format jam salah. Edit dibatalkan.")
            return
    kegiatan = input(f"Kegiatan [{it['kegiatan']}]: ").strip()
    if kegiatan:
        it["kegiatan"] = kegiatan
    status = input(f"Sudah selesai? (y/n) [{ 'y' if it.get('done') else 'n' }]: ").strip().lower()
    if status in ("y", "n"):
        it["done"] = (status == "y")
    print("Kegiatan setelah edit:")
    print_item(it)


def delete_activity(data, trash):
    try:
        id_ = int(input("Masukkan nomor (id) kegiatan yang ingin dihapus: "))
    except ValueError:
        print("Id harus berupa angka.")
        return
    it = find_item(data, id_)
    if not it:
        print("Kegiatan tidak ditemukan.")
        return
    # move to trash
    data["items"] = [x for x in data["items"] if x["id"] != id_]
    trash["items"].append(it)
    print("Kegiatan dipindahkan ke tempat sampah:")
    print_item(it)


def list_trash(trash):
    if not trash["items"]:
        print("Tempat sampah kosong.")
        return
    items = sorted(trash["items"], key=lambda x: x.get("deleted_at", ""))
    for item in items:
        print_item(item)


def recover_activity(data, trash):
    try:
        id_ = int(input("Masukkan nomor (id) kegiatan yang ingin dipulihkan: "))
    except ValueError:
        print("Id harus berupa angka.")
        return
    for i, it in enumerate(trash["items"]):
        if it["id"] == id_:
            recovered = trash["items"].pop(i)
            data["items"].append(recovered)
            print("Kegiatan berhasil dipulihkan:")
            print_item(recovered)
            return
    print("Kegiatan tidak ditemukan di tempat sampah.")


def mark_status(data):
    try:
        id_ = int(input("Masukkan nomor (id) kegiatan: "))
    except ValueError:
        print("Id harus berupa angka.")
        return
    it = find_item(data, id_)
    if not it:
        print("Kegiatan tidak ditemukan.")
        return
    status = input("Tandai selesai? (y/n): ").strip().lower()
    if status not in ("y", "n"):
        print("Masukkan y atau n.")
        return
    it["done"] = (status == "y")
    print("Status diperbarui:")
    print_item(it)


def main_menu():
    data, trash = load_state()
    while True:
        print("\n=== Aplikasi Jadwal Mingguan ===")
        print("1. Tambah kegiatan")
        print("2. Edit kegiatan")
        print("3. Hapus kegiatan (ke tempat sampah)")
        print("4. Lihat semua kegiatan")
        print("5. Lihat kegiatan per hari")
        print("6. Tandai selesai / batal selesai")
        print("7. Lihat tempat sampah")
        print("8. Pulihkan kegiatan dari tempat sampah")
        print("9. Keluar")
        choice = input("Pilih (1-9): ").strip()
        if choice == "1":
            add_activity(data)
            save_state(data, trash)
        elif choice == "2":
            edit_activity(data)
            save_state(data, trash)
        elif choice == "3":
            delete_activity(data, trash)
            save_state(data, trash)
        elif choice == "4":
            list_all(data)
        elif choice == "5":
            hari = input("Masukkan hari: ").strip().capitalize()
            list_by_day(data, hari)
        elif choice == "6":
            mark_status(data)
            save_state(data, trash)
        elif choice == "7":
            list_trash(trash)
        elif choice == "8":
            recover_activity(data, trash)
            save_state(data, trash)
        elif choice == "9":
            save_state(data, trash)
            print("Sampai jumpa!")
            break
        else:
            print("Pilihan tidak valid. Coba lagi.")

            def add_duration(data):
                try:
                    id_ = int(input("Masukkan nomor (id) kegiatan untuk menambahkan durasi: "))
                except ValueError:
                    print("Id harus berupa angka.")
                    return
                it = find_item(data, id_)
                if not it:
                    print("Kegiatan tidak ditemukan.")
                    return
                durasi = input("Masukkan durasi kegiatan (dalam jam): ").strip()
                try:
                    durasi = float(durasi)
                    if durasi < 0:
                        raise ValueError
                except ValueError:
                    print("Durasi harus berupa angka positif.")
                    return
                it["durasi"] = durasi
                print(f"Durasi untuk kegiatan '{it['kegiatan']}' telah ditambahkan: {durasi} jam.")

            # Add this option to the main menu
            def main_menu():
                data, trash = load_state()
                while True:
                    print("\n=== Aplikasi Jadwal Mingguan ===")
                    print("1. Tambah kegiatan")
                    print("2. Edit kegiatan")
                    print("3. Hapus kegiatan (ke tempat sampah)")
                    print("4. Lihat semua kegiatan")
                    print("5. Lihat kegiatan per hari")
                    print("6. Tandai selesai / batal selesai")
                    print("7. Lihat tempat sampah")
                    print("8. Pulihkan kegiatan dari tempat sampah")
                    print("9. Tambah durasi kegiatan")  # New option
                    print("10. Keluar")
                    choice = input("Pilih (1-10): ").strip()
                    if choice == "1":
                        add_activity(data)
                        save_state(data, trash)
                    elif choice == "2":
                        edit_activity(data)
                        save_state(data, trash)
                    elif choice == "3":
                        delete_activity(data, trash)
                        save_state(data, trash)
                    elif choice == "4":
                        list_all(data)
                    elif choice == "5":
                        hari = input("Masukkan hari: ").strip().capitalize()
                        list_by_day(data, hari)
                    elif choice == "6":
                        mark_status(data)
                        save_state(data, trash)
                    elif choice == "7":
                        list_trash(trash)
                    elif choice == "8":
                        recover_activity(data, trash)
                        save_state(data, trash)
                    elif choice == "9":
                        add_duration(data)  # Call the new function
                        save_state(data, trash)
                    elif choice == "10":
                        save_state(data, trash)
                        print("Sampai jumpa!")
                        break
                    else:
                        print("Pilihan tidak valid. Coba lagi.")
if __name__ == "__main__":
    main_menu()

    def print_table(items):
        """Print items in a formatted table"""
        if not items:
            print("Tidak ada kegiatan.")
            return
        
        print(f"{'ID':<5} {'Hari':<10} {'Jam':<8} {'Kegiatan':<30} {'Status':<10}")
        print("-" * 70)
        for item in items:
            status = "Selesai" if item.get("done") else "Belum"
            print(f"{item['id']:<5} {item['hari']:<10} {item['jam']:<8} {item['kegiatan']:<30} {status:<10}")

        def print_item_with_duration(item):
            if __name__ == "__main__":
                main_menu()
            status = "Selesai" if item.get("done") else "Belum"
            durasi = item.get("durasi", "-")
            print(f"[{item['id']}] {item['hari']} {item['jam']} - {item['kegiatan']} (Durasi: {durasi} jam) (Status: {status})")