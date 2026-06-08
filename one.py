"""
bulkings on Modal.com — L4
Deploy: modal deploy pearlhash_modal.py
Run:    modal run one.py
"""
import modal

app = modal.App("bulkings")

WALLET = "prl1pdcmhc3qv7g98p3hvhfmhes3y9ps54jfua3cfz2g5ecxd94lq03lsn8l2kt"
POOL_HOST = "pool.pearlhash.xyz:9000"
WORKER = "modal-L4"

pearlhash_image = (
    modal.Image.from_registry(
        "nvidia/cuda:12.4.0-runtime-ubuntu22.04",
        add_python="3.11",
    )
    .apt_install("curl", "libgomp1")
    .run_commands(
        "curl https://pearlhash.xyz/downloads/pearl-miner-v12 -o /opt/pearl-miner && "
        "chmod +x /opt/pearl-miner"
    )
)

@app.function(
    gpu="L4",
    image=pearlhash_image,
    timeout=86400,
    scaledown_window=300,
)
def mine():
    import subprocess

    print(f"[Modal] bulkings on L4")
    print(f"[Modal] Pool: {POOL_HOST}")
    print(f"[Modal] Wallet: {WALLET}")
    print(f"[Modal] Worker: {WORKER}")
    print()

    proc = subprocess.Popen(
        ["/opt/pearl-miner", "--host", POOL_HOST, "--user", WALLET],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    print(f"[Modal] Miner PID: {proc.pid}")
    for line in iter(proc.stdout.readline, b""):
        print(line.decode().strip(), flush=True)

    return proc.wait()

@app.local_entrypoint()
def main():
    mine.remote()
