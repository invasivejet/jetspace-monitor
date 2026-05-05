from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID


CERT_DIR = Path(__file__).resolve().parents[1] / "certs"


def write_key(path: Path, key: rsa.RSAPrivateKey) -> None:
    path.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )


def write_cert(path: Path, cert: x509.Certificate) -> None:
    path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))


def make_name(common_name: str) -> x509.Name:
    return x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Jetspace"),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ]
    )


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def build_ca() -> tuple[rsa.RSAPrivateKey, x509.Certificate]:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = make_name("Jetspace Root CA")
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now_utc() - timedelta(days=1))
        .not_valid_after(now_utc() + timedelta(days=3650))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(private_key=key, algorithm=hashes.SHA256())
    )
    return key, cert


def build_leaf(
    common_name: str,
    ca_key: rsa.RSAPrivateKey,
    ca_cert: x509.Certificate,
    is_server: bool,
) -> tuple[rsa.RSAPrivateKey, x509.Certificate]:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    eku = [ExtendedKeyUsageOID.SERVER_AUTH] if is_server else [ExtendedKeyUsageOID.CLIENT_AUTH]
    builder = (
        x509.CertificateBuilder()
        .subject_name(make_name(common_name))
        .issuer_name(ca_cert.subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now_utc() - timedelta(days=1))
        .not_valid_after(now_utc() + timedelta(days=825))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(x509.ExtendedKeyUsage(eku), critical=False)
    )
    if is_server:
        builder = builder.add_extension(
            x509.SubjectAlternativeName([x509.DNSName("localhost"), x509.IPAddress(__import__("ipaddress").ip_address("127.0.0.1"))]),
            critical=False,
        )
    cert = builder.sign(private_key=ca_key, algorithm=hashes.SHA256())
    return key, cert


def main() -> None:
    CERT_DIR.mkdir(parents=True, exist_ok=True)
    ca_key, ca_cert = build_ca()
    server_key, server_cert = build_leaf("jetspace-windows-server", ca_key, ca_cert, is_server=True)
    client_key, client_cert = build_leaf("jetspace-ubuntu-client", ca_key, ca_cert, is_server=False)

    write_key(CERT_DIR / "ca.key", ca_key)
    write_cert(CERT_DIR / "ca.crt", ca_cert)
    write_key(CERT_DIR / "server.key", server_key)
    write_cert(CERT_DIR / "server.crt", server_cert)
    write_key(CERT_DIR / "client.key", client_key)
    write_cert(CERT_DIR / "client.crt", client_cert)

    print(f"Certificates written to {CERT_DIR}")


if __name__ == "__main__":
    main()
