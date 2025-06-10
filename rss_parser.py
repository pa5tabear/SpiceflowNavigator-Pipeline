from xml.etree import ElementTree as ET

class RSSParser:
    """Minimal RSS parser extracting enclosure URLs."""

    def extract_audio_urls(self, xml_content: str) -> list[str]:
        root = ET.fromstring(xml_content)
        urls = []
        for enclosure in root.findall('.//enclosure'):
            url = enclosure.attrib.get('url')
            if url:
                urls.append(url)
        return urls
