class AddressUtils:
    def __init__(self, w3_instance):
        self.w3 = w3_instance

    def addr_checksum(self, addr: str) -> str:
        return self.w3.to_checksum_address(addr)

    @staticmethod
    def addr_to_hex(addr: str) -> str:
        return "0x" + "0" * 24 + addr[2:]

    @staticmethod
    def clean_address(addr: str) -> str:
        """Strips leading zeroes from Ethereum addresses and returns the 0x-prefixed clean address."""
        return "0x" + addr[-40:]
