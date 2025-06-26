# src/tools.py
def check_printer_status(ip_address: str) -> str:
    """
    SIMULAÇÃO: Verifica se um dispositivo em um determinado endereço IP está online.
    Retorna 'Online' para IPs que terminam em número par e 'Offline' para ímpares.
    """
    print(f"--- SIMULANDO FERRAMENTA: check_printer_status para o IP {ip_address} ---")
    try:
        last_octet = int(ip_address.split('.')[-1])
        if last_octet % 2 == 0:
            return "Online"
        else:
            return "Offline"
    except (ValueError, IndexError):
        return "Erro: Endereço de IP inválido."