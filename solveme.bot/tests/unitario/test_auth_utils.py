# solveme_bot/tests/unitario/test_auth_utils.py
import pytest
from backend.src.auth_utils import get_password_hash, verify_password

def test_get_password_hash_returns_string():
    """Verifica se get_password_hash retorna uma string não vazia."""
    password = "minhasenhaforte123"
    hashed_password = get_password_hash(password)
    assert isinstance(hashed_password, str)
    assert len(hashed_password) > 0
    assert hashed_password != password # O hash não deve ser igual à senha original

def test_verify_password_correct_password():
    """Verifica se verify_password retorna True para senha correta."""
    password = "minhasenhaforte123"
    hashed_password = get_password_hash(password)
    assert verify_password(password, hashed_password) is True

def test_verify_password_incorrect_password():
    """Verifica se verify_password retorna False para senha incorreta."""
    password = "minhasenhaforte123"
    hashed_password = get_password_hash(password)
    assert verify_password("senhaincorreta", hashed_password) is False

def test_get_password_hash_different_hashes_for_same_password():
    """Verifica se o hash é diferente a cada chamada para a mesma senha (devido ao salt)."""
    password = "outrasenha123"
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)
    assert hash1 != hash2 # Hashes devem ser diferentes devido ao salt, mas verificarão a mesma senha
    assert verify_password(password, hash1) is True
    assert verify_password(password, hash2) is True