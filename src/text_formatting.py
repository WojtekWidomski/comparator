# text_formatting.py
#
# Copyright 2022 Wojtek Widomski
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import random

class Formatting():
    """Text formatting"""

    wrap_char_number = 50
    space_wrap_char_number = 40
    obfuscated_characters = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!#$%'()*+,-./:=?@^_`{|}~"

    def paragraph_to_pango_markup(self, text):
        formatting_codes = {
            "l": "b", #bold
            "m": "s", #strikethrough
            "n": "u", #underline
            "o": "i"  #italic
        }
        colors = {
            "0": "000000", #black
            "1": "0000AA", #dark_blue
            "2": "00AA00", #dark_green
            "3": "00AAAA", #dark_aqua
            "4": "AA0000", #dark_red
            "5": "AA00AA", #dark_purple
            "6": "FFAA00", #gold
            "7": "AAAAAA", #gray
            "8": "555555", #dark_gray
            "9": "5555FF", #blue
            "a": "55FF55", #green
            "b": "55FFFF", #aqua
            "c": "FF5555", #red
            "d": "FF55FF", #light_purple
            "e": "FFFF55", #yellow
            "f": "FFFFFF"  #white
        }
        open_tags = []
        split_text = text.split("§")
        formatted = split_text[0]

        for fragment in split_text[1:]:
            if fragment[0] == "r":
                for i in range(len(open_tags)):
                    formatted += ("</" + open_tags.pop(len(open_tags)-1) + ">")
                formatted += fragment[1:]
            elif fragment[0] in list(formatting_codes):
                tag = formatting_codes[fragment[0]]
                open_tags.append(tag)
                formatted += ("<" + tag + ">" + fragment[1:])
            elif fragment[0] == "k":
                open_tags.append("span")
                # "§" is used as obfuscated in formatted text
                formatted += ("<span font_family='monospace'>" + len(fragment[1:])*"§")
            else:
                for i in range(len(open_tags)):
                    formatted += ("</" + open_tags.pop(len(open_tags)-1) + ">")
                color = colors[fragment[0]]
                open_tags.append("span")
                formatted += ("<span foreground='#" + color + "'>" + fragment[1:])

        for i in range(len(open_tags)):
            formatted += ("</" + open_tags.pop(len(open_tags)-1) + ">")

        return formatted

    def json_to_pango_markup(self, text):
        formatting_tags = {
            "bold": "weight='bold'",
            "italic": "style='italic'",
            "underlined": "underline='single'",
            "strikethrough": "strikethrough='true'",
            "obfuscated" : "font_family='monospace'"
        }
        colors = {
            "black": "000000",
            "dark_blue": "0000AA",
            "dark_green": "00AA00",
            "dark_aqua": "00AAAA",
            "dark_red": "AA0000",
            "dark_purple": "AA00AA",
            "gold": "FFAA00",
            "gray": "AAAAAA",
            "dark_gray": "555555",
            "blue": "5555FF",
            "green": "55FF55",
            "aqua": "55FFFF",
            "red": "FF5555",
            "light_purple": "FF55FF",
            "yellow": "FFFF55",
            "white": "FFFFFF"
        }
        formatted = ""

        if "text" in text:
            formatted += self.paragraph_to_pango_markup(text["text"])
        if "extra" in text:
            for fragment in text["extra"]:
                formatted += "<span "
                for tag in fragment:
                    if tag in formatting_tags and fragment[tag]:
                        formatted += formatting_tags[tag]
                    elif tag == "color":
                        formatted += "foreground='#" + colors[fragment[tag]] + "'"
                if "obfuscated" in fragment and fragment['obfuscated']:
                    formatted += ">" + len(fragment['text'])*"§" + "</span>"
                else:
                    formatted += ">" + fragment['text'] + "</span>"

        return formatted

    def wrap_pango_markup(self, text):
        count = True
        spaces = 0
        char_number = 0
        for i in range(len(text)):
            if text[i] == "<":
                count = False
            if count:
                char_number += 1
            if text[i] == ">":
                count = True
            if char_number >= self.wrap_char_number:
                char_number = i
                break
            if char_number >= self.space_wrap_char_number:
                if text[i]==" ":
                    spaces += 1
                else:
                    if spaces >= 5:
                        char_number = i
                        break
                    spaces = 0
        if char_number > self.wrap_char_number:
            wrapped = (text[:char_number] + "\n" + text[char_number:])
        else:
            wrapped = text+"\n"
        return wrapped

    def remove_spaces(self, text):
        words_list = []
        for line in text.split("\n"):
            words_list.append(" ".join(line.split()))
        removed_spaces = "\n".join(words_list)
        # TODO: Use str.removeprefix
        if removed_spaces.startswith("<span > </span>"):
            removed_spaces = removed_spaces.replace("<span > </span>", "", 1)
        return removed_spaces

    def auto(self, text, wrap=True, remove_spaces=True):
        if type(text) is dict:
            pango_markup = self.json_to_pango_markup(text)
        else:
            pango_markup = self.paragraph_to_pango_markup(text)
        if wrap and (not "\n" in pango_markup):
            pango_markup = self.wrap_pango_markup(pango_markup)
        if remove_spaces:
            pango_markup = self.remove_spaces(pango_markup)
        return pango_markup

    def obfuscated_text(self, text):
        while("§" in text):
            text = text.replace("§", random.choice(self.obfuscated_characters), 1)
        return text
