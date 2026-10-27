"""Tests unitarios de la lógica de cálculo."""

import pytest

from app.pricing import QuoteError, calculate_quote


def test_servicio_sin_extras():
    assert calculate_quote("manicura-simple", []) == {"total_price": 25, "total_duration_minutes": 45}


def test_ejemplo_del_readme():
    # Manicura BIAB + francesa + diseño en 2 uñas = 54 € y 100 min
    extras = [{"extra_id": "francesa"}, {"extra_id": "diseno", "nails": 2}]
    assert calculate_quote("manicura-biab", extras) == {"total_price": 54, "total_duration_minutes": 100}


def test_extra_por_una_se_multiplica():
    result = calculate_quote("pedicura-simple", [{"extra_id": "reparacion", "nails": 3}])
    assert result == {"total_price": 35 + 9, "total_duration_minutes": 60 + 30}


def test_servicio_desconocido():
    with pytest.raises(QuoteError):
        calculate_quote("no-existe", [])


def test_extra_desconocido():
    with pytest.raises(QuoteError):
        calculate_quote("manicura-simple", [{"extra_id": "no-existe"}])


@pytest.mark.parametrize("nails", [None, 0, 11])
def test_extra_por_una_con_numero_invalido(nails):
    with pytest.raises(QuoteError):
        calculate_quote("manicura-simple", [{"extra_id": "diseno", "nails": nails}])
