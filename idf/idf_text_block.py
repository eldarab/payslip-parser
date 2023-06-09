from business_logic.text_block import TextBlock


class IDFTextBlock(TextBlock):
    def _parse_text(self, raw_text, reverse_alphas=True):
        text = raw_text.strip('\n').replace('\xa0', ' ')

        alphas = ''
        numbers = ''
        for idx, char in enumerate(text):
            if char.isnumeric():
                numbers += char
            elif char == '.' and text[idx - 1].isnumeric() and text[idx + 1].isnumeric():
                numbers += char
            else:
                alphas = char + alphas if reverse_alphas else alphas + char

        return {'alphas': alphas, 'numbers': numbers}
