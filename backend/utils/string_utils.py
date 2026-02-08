"""
String processing utilities.
These utilities provide common string operations and manipulations across the application.
"""

import re
from typing import List, Optional, Union
from datetime import datetime


class StringUtils:
    """
    Utility class for string processing operations.
    Provides common string manipulations, formatting, and processing functions.
    """

    @staticmethod
    def capitalize_words(text: str) -> str:
        """
        Capitalize the first letter of each word in a string.

        Args:
            text: Input string to capitalize

        Returns:
            String with capitalized words
        """
        if not text:
            return text

        # Split on whitespace and capitalize each word
        words = text.split()
        capitalized_words = [word.capitalize() for word in words]
        return ' '.join(capitalized_words)

    @staticmethod
    def snake_case_to_camel_case(snake_str: str) -> str:
        """
        Convert snake_case string to camelCase.

        Args:
            snake_str: Snake case string to convert

        Returns:
            Camel case string
        """
        if not snake_str:
            return snake_str

        components = snake_str.split('_')
        # Capitalize the first letter of each component except the first one
        return components[0] + ''.join(x.capitalize() for x in components[1:])

    @staticmethod
    def camel_case_to_snake_case(camel_str: str) -> str:
        """
        Convert camelCase string to snake_case.

        Args:
            camel_str: Camel case string to convert

        Returns:
            Snake case string
        """
        if not camel_str:
            return camel_str

        # Insert underscores before uppercase letters that follow lowercase letters
        s1 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', camel_str)
        return s1.lower()

    @staticmethod
    def kebab_case_to_camel_case(kebab_str: str) -> str:
        """
        Convert kebab-case string to camelCase.

        Args:
            kebab_str: Kebab case string to convert

        Returns:
            Camel case string
        """
        if not kebab_str:
            return kebab_str

        components = kebab_str.split('-')
        # Capitalize the first letter of each component except the first one
        return components[0] + ''.join(x.capitalize() for x in components[1:])

    @staticmethod
    def camel_case_to_kebab_case(camel_str: str) -> str:
        """
        Convert camelCase string to kebab-case.

        Args:
            camel_str: Camel case string to convert

        Returns:
            Kebab case string
        """
        if not camel_str:
            return camel_str

        # Insert hyphens before uppercase letters that follow lowercase letters
        s1 = re.sub('([a-z0-9])([A-Z])', r'\1-\2', camel_str)
        return s1.lower()

    @staticmethod
    def truncate(text: str, length: int, suffix: str = '...') -> str:
        """
        Truncate a string to a specified length with a suffix.

        Args:
            text: String to truncate
            length: Maximum length of the string
            suffix: Suffix to append to truncated string

        Returns:
            Truncated string with suffix if necessary
        """
        if not text or len(text) <= length:
            return text

        suffix_len = len(suffix)
        return text[:length - suffix_len] + suffix

    @staticmethod
    def remove_extra_whitespace(text: str) -> str:
        """
        Remove extra whitespace from a string.

        Args:
            text: Input string

        Returns:
            String with normalized whitespace
        """
        if not text:
            return text

        # Replace multiple whitespace characters with single space
        return re.sub(r'\s+', ' ', text).strip()

    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """
        Normalize whitespace characters in a string (spaces, tabs, newlines).

        Args:
            text: Input string

        Returns:
            String with normalized whitespace
        """
        if not text:
            return text

        # Replace all whitespace characters with single space
        return ' '.join(text.split())

    @staticmethod
    def sanitize_html(text: str) -> str:
        """
        Remove HTML tags from a string.

        Args:
            text: Input string that may contain HTML

        Returns:
            String with HTML tags removed
        """
        if not text:
            return text

        # Remove HTML tags
        clean_text = re.sub(r'<[^>]*>', '', text)
        # Clean up any extra whitespace created
        return StringUtils.normalize_whitespace(clean_text)

    @staticmethod
    def strip_tags(text: str) -> str:
        """
        Alias for sanitize_html method.

        Args:
            text: Input string that may contain HTML

        Returns:
            String with HTML tags removed
        """
        return StringUtils.sanitize_html(text)

    @staticmethod
    def extract_emails(text: str) -> List[str]:
        """
        Extract email addresses from a string.

        Args:
            text: Input string that may contain emails

        Returns:
            List of extracted email addresses
        """
        if not text:
            return []

        # Regular expression for email extraction
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(email_pattern, text)

    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """
        Extract URLs from a string.

        Args:
            text: Input string that may contain URLs

        Returns:
            List of extracted URLs
        """
        if not text:
            return []

        # Regular expression for URL extraction
        url_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?'
        return re.findall(url_pattern, text)

    @staticmethod
    def mask_email(email: str) -> str:
        """
        Mask an email address for privacy.

        Args:
            email: Email address to mask

        Returns:
            Masked email address
        """
        if not email:
            return email

        try:
            local_part, domain = email.rsplit('@', 1)
            if len(local_part) <= 2:
                masked_local = local_part[0] + '*' * max(0, len(local_part) - 1)
            else:
                masked_local = local_part[0] + '*' * (len(local_part) - 2) + local_part[-1]

            return f"{masked_local}@{domain}"
        except ValueError:
            # If email doesn't contain '@', return as is
            return email

    @staticmethod
    def pluralize(word: str, count: int, plural_suffix: str = 's') -> str:
        """
        Pluralize a word based on count.

        Args:
            word: Word to pluralize
            count: Count to determine if plural form should be used
            plural_suffix: Suffix to add for pluralization (default 's')

        Returns:
            Pluralized word if count is not 1, otherwise the original word
        """
        if count == 1:
            return word
        else:
            # Handle common irregular plurals
            if word.lower() == 'person':
                return 'people'
            elif word.lower() == 'child':
                return 'children'
            elif word.lower() == 'man':
                return 'men'
            elif word.lower() == 'woman':
                return 'women'
            elif word.lower() == 'goose':
                return 'geese'
            elif word.lower() == 'foot':
                return 'feet'
            elif word.lower() == 'tooth':
                return 'teeth'
            elif word.lower() == 'mouse':
                return 'mice'

            # For regular nouns
            return word + plural_suffix

    @staticmethod
    def slugify(text: str, separator: str = '-') -> str:
        """
        Convert a string to a URL-safe slug.

        Args:
            text: Input string to slugify
            separator: Separator character to use (default is hyphen)

        Returns:
            Slugified string
        """
        if not text:
            return ''

        # Convert to lowercase and replace non-alphanumeric characters with separator
        slug = re.sub(r'[^\w\s-]', ' ', text.lower())
        # Replace spaces with separator
        slug = re.sub(r'[-\s]+', separator, slug)
        # Remove leading/trailing separators
        return slug.strip(separator)

    @staticmethod
    def word_count(text: str) -> int:
        """
        Count the number of words in a string.

        Args:
            text: Input string

        Returns:
            Number of words in the string
        """
        if not text:
            return 0

        # Split on whitespace and count non-empty parts
        words = text.split()
        return len([word for word in words if word.strip()])

    @staticmethod
    def line_count(text: str) -> int:
        """
        Count the number of lines in a string.

        Args:
            text: Input string

        Returns:
            Number of lines in the string
        """
        if not text:
            return 0

        return len(text.splitlines())

    @staticmethod
    def character_count(text: str, include_spaces: bool = True) -> int:
        """
        Count the number of characters in a string.

        Args:
            text: Input string
            include_spaces: Whether to include spaces in the count

        Returns:
            Number of characters in the string
        """
        if not text:
            return 0

        if include_spaces:
            return len(text)
        else:
            # Count characters excluding spaces
            return len(text.replace(' ', '').replace('\t', '').replace('\n', '').replace('\r', ''))

    @staticmethod
    def reverse(text: str) -> str:
        """
        Reverse a string.

        Args:
            text: Input string

        Returns:
            Reversed string
        """
        return text[::-1]

    @staticmethod
    def pad_left(text: str, length: int, char: str = ' ') -> str:
        """
        Left-pad a string to a specified length.

        Args:
            text: Input string
            length: Desired length of the string
            char: Character to use for padding (default is space)

        Returns:
            Left-padded string
        """
        if not text:
            return char * length

        if len(text) >= length:
            return text

        return char * (length - len(text)) + text

    @staticmethod
    def pad_right(text: str, length: int, char: str = ' ') -> str:
        """
        Right-pad a string to a specified length.

        Args:
            text: Input string
            length: Desired length of the string
            char: Character to use for padding (default is space)

        Returns:
            Right-padded string
        """
        if not text:
            return char * length

        if len(text) >= length:
            return text

        return text + char * (length - len(text))

    @staticmethod
    def pad_center(text: str, length: int, char: str = ' ') -> str:
        """
        Center-pad a string to a specified length.

        Args:
            text: Input string
            length: Desired length of the string
            char: Character to use for padding (default is space)

        Returns:
            Center-padded string
        """
        if not text:
            return char * length

        if len(text) >= length:
            return text

        padding = length - len(text)
        left_padding = padding // 2
        right_padding = padding - left_padding

        return char * left_padding + text + char * right_padding

    @staticmethod
    def is_palindrome(text: str) -> bool:
        """
        Check if a string is a palindrome (ignoring case and non-alphanumeric characters).

        Args:
            text: Input string to check

        Returns:
            True if the string is a palindrome, False otherwise
        """
        if not text:
            return True

        # Remove non-alphanumeric characters and convert to lowercase
        cleaned_text = re.sub(r'[^A-Za-z0-9]', '', text.lower())
        return cleaned_text == cleaned_text[::-1]

    @staticmethod
    def generate_acronym(text: str) -> str:
        """
        Generate an acronym from a phrase.

        Args:
            text: Input phrase

        Returns:
            Acronym generated from the first letter of each word
        """
        if not text:
            return ''

        # Split by spaces and punctuation, take first letter of each word
        words = re.split(r'\W+', text)
        acronym = ''.join(word[0].upper() for word in words if word)
        return acronym

    @staticmethod
    def count_occurrences(text: str, substring: str, case_sensitive: bool = True) -> int:
        """
        Count occurrences of a substring in a text.

        Args:
            text: Input string to search in
            substring: Substring to count
            case_sensitive: Whether to perform case-sensitive search

        Returns:
            Number of occurrences of the substring in the text
        """
        if not text or not substring:
            return 0

        if case_sensitive:
            return text.count(substring)
        else:
            return text.lower().count(substring.lower())

    @staticmethod
    def replace_nth_occurrence(text: str, old: str, new: str, n: int) -> str:
        """
        Replace the nth occurrence of a substring in a text.

        Args:
            text: Input string to perform replacement in
            old: Substring to replace
            new: Replacement substring
            n: Which occurrence to replace (1-indexed)

        Returns:
            Text with the nth occurrence replaced
        """
        if not text or not old or n <= 0:
            return text

        # Find all occurrences
        occurrences = []
        start = 0
        while True:
            pos = text.find(old, start)
            if pos == -1:
                break
            occurrences.append(pos)
            start = pos + 1

        # If n is greater than number of occurrences, return original text
        if n > len(occurrences):
            return text

        # Replace the nth occurrence
        pos = occurrences[n - 1]
        return text[:pos] + new + text[pos + len(old):]

    @staticmethod
    def highlight_keywords(text: str, keywords: List[str], highlight_template: str = '<mark>{}</mark>') -> str:
        """
        Highlight keywords in a text with a template.

        Args:
            text: Input string to highlight keywords in
            keywords: List of keywords to highlight
            highlight_template: Template to wrap highlighted keywords (default is HTML mark tag)

        Returns:
            Text with keywords highlighted according to the template
        """
        if not text or not keywords:
            return text

        result = text
        for keyword in keywords:
            # Use word boundaries to match complete words only
            pattern = r'\b' + re.escape(keyword) + r'\b'
            replacement = highlight_template.format(keyword)
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

        return result