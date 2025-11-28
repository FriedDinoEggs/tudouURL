class ShortUrlService:
    CHAR_SET = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    BASE = len(CHAR_SET)

    @classmethod
    def encode(cls, id_num: int) -> str:
        if id_num == 0:
            return cls.CHAR_SET[0]

        short_code = ''
        base_id = id_num
        while base_id > 0:
            char_index = base_id % cls.BASE
            short_code += cls.CHAR_SET[char_index]
            base_id //= cls.BASE

        return short_code

    @classmethod
    def decode(cls, short_code: str) -> int:
        original_id = 0
        char_to_index = {char: i for i, char in enumerate(cls.CHAR_SET)}

        for i, char in enumerate(short_code):
            char_value = char_to_index.get(char)
            if char_value is None:
                raise ValueError(f"Invalid character '{char}' in short_code '{short_code}'")

            original_id += char_value * (cls.BASE**i)

        return original_id
