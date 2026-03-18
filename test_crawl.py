import unittest
from crawl import normalize_url, get_heading_from_html, get_first_paragraph_from_html, get_urls_from_html, get_images_from_html, extract_page_data


class TestCrawl(unittest.TestCase):
    def test_normalize_url(self):
        input_url = "https://www.boot.dev/blog/path"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)

    def test_normalize_url_trailing_slash(self):
        input_url = "https://www.boot.dev/blog/path/"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)

    def test_normalize_url_root_path(self):
        input_url = "https://www.boot.dev/"
        actual = normalize_url(input_url)
        expected = "www.boot.dev"
        self.assertEqual(actual, expected)

    def test_normalize_url_no_path(self):
        input_url = "https://www.boot.dev"
        actual = normalize_url(input_url)
        expected = "www.boot.dev"
        self.assertEqual(actual, expected)

    def test_get_heading_from_html_basic(self):
        input_body = '<html><body><h1>Test Title</h1></body></html>'
        actual = get_heading_from_html(input_body)
        expected = "Test Title"
        self.assertEqual(actual, expected)

    def test_get_heading_from_html_none(self):
        input_body = '<html><body><p>No heading here</p></body></html>'
        actual = get_heading_from_html(input_body)
        expected = None
        self.assertEqual(actual, expected)

    def test_get_heading_from_html_multiple(self):
        input_body = '<html><body><h1>First</h1><h1>Second</h1></body></html>'
        actual = get_heading_from_html(input_body)
        expected = "First"
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_main_priority(self):
        input_body = '''<html><body>
            <p>Outside paragraph.</p>
            <main>
                <p>Main paragraph.</p>
            </main>
        </body></html>'''
        actual = get_first_paragraph_from_html(input_body)
        expected = "Outside paragraph."
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_none(self):
        input_body = '<html><body><h1>Only heading</h1></body></html>'
        actual = get_first_paragraph_from_html(input_body)
        expected = None
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_with_whitespace(self):
        input_body = '<html><body><p>Paragraph with spaces</p></body></html>'
        actual = get_first_paragraph_from_html(input_body)
        expected = "Paragraph with spaces"
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_absolute(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><a href="https://crawler-test.com"><span>Boot.dev</span></a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com"]
        self.assertEqual(actual, expected)
    
    def test_get_urls_from_html_relative(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><a href="/path"><span>Boot.dev</span></a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/path"]
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_multiple(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><a href="/path1">Link1</a><a href="/path2">Link2</a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/path1", "https://crawler-test.com/path2"]
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_none(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><p>No links here</p></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = []
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_mixed(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><a href="https://other-site.com">Other</a><a href="/local">Local</a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://other-site.com", "https://crawler-test.com/local"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_relative(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img src="/logo.png" alt="Logo"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/logo.png"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_absolute(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img src="https://cdn.example.com/image.jpg" alt="Image"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://cdn.example.com/image.jpg"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_multiple(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img src="/img1.png"><img src="/img2.jpg"><img src="https://other.com/img3.gif"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/img1.png", "https://crawler-test.com/img2.jpg", "https://other.com/img3.gif"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_none(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><p>No images here</p></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = []
        self.assertEqual(actual, expected)
        def test_extract_page_data_complete(self):
            input_url = "https://example.com"
            input_body = '''<html><body>
                <h1>Page Title</h1>
                <p>First paragraph text.</p>
                <a href="/about">About</a>
                <a href="https://other.com">Other</a>
                <img src="/logo.png" alt="Logo">
                <img src="https://cdn.com/image.jpg" alt="Image">
            </body></html>'''
            actual = extract_page_data(input_body, input_url)
            expected = {
                "url": "example.com",
                "heading": "Page Title",
                "first_paragraph": "First paragraph text.",
                "outgoing_links": ["https://example.com/about", "https://other.com"],
                "image_urls": ["https://example.com/logo.png", "https://cdn.com/image.jpg"]
            }
            self.assertEqual(actual, expected)

        def test_extract_page_data_minimal(self):
            input_url = "https://example.com/page"
            input_body = '<html><body><p>Content</p></body></html>'
            actual = extract_page_data(input_body, input_url)
            expected = {
                "url": "example.com/page",
                "heading": None,
                "first_paragraph": "Content",
                "outgoing_links": [],
                "image_urls": []
            }
            self.assertEqual(actual, expected)

        def test_extract_page_data_no_content(self):
            input_url = "https://example.com"
            input_body = '<html><body></body></html>'
            actual = extract_page_data(input_body, input_url)
            expected = {
                "url": "example.com",
                "heading": None,
                "first_paragraph": None,
                "outgoing_links": [],
                "image_urls": []
            }
            self.assertEqual(actual, expected)

        def test_extract_page_data_trailing_slash(self):
            input_url = "https://example.com/blog/"
            input_body = '<html><body><h1>Blog</h1><p>Post</p></body></html>'
            actual = extract_page_data(input_body, input_url)
            expected = {
                "url": "example.com/blog",
                "heading": "Blog",
                "first_paragraph": "Post",
                "outgoing_links": [],
                "image_urls": []
            }
            self.assertEqual(actual, expected)
            
if __name__ == "__main__":
    unittest.main()