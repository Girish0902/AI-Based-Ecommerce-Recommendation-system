import reflex as rx
from dotenv import load_dotenv
from reflex.plugins.sitemap import SitemapPlugin

load_dotenv()

config = rx.Config(
    app_name="app",
    plugins=[SitemapPlugin()],
)
