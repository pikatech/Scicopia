from scicopia.app.main.views import split_prefix

def test_no_space():
    """No space in the entire string."""
    text = "Test"
    expected = ("", "Test")
    assert split_prefix(text) == expected

def test_ends_space():
    """The string ends with a space, otherwise no spaces."""
    text = "Test "
    expected = ("", "Test ")
    assert split_prefix(text) == expected

def test_one_space():
    """The string contains a space separating two words."""
    text = "Test me"
    expected = ("", "Test me")
    assert split_prefix(text) == expected

def test_one_space_ends_space():
    """There's one space as a separator and one at the end."""
    text = "Test me "
    expected = ("Test ", "me ")
    assert split_prefix(text) == expected

def test_three_words():
    """There are two spaces as separators and none at the end."""
    text = "Test me now"
    expected = ("Test ", "me now")
    assert split_prefix(text) == expected

def test_three_words_ends_space():
    """There are two spaces as separators and one at the end."""
    text = "Test me now "
    expected = ("Test me ", "now ")
    assert split_prefix(text) == expected
