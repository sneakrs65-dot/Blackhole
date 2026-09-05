"""
Blackhole Browser
------------------
A simple tabbed web browser built with PyQt5 + QtWebEngine.
Color scheme: Coral (#FF6F5E), Orange (#FF8C42), Black (#121212).

Install dependencies:
    pip install PyQt5 PyQtWebEngine
"""

import sys
from PyQt5.QtCore import QSize, QUrl, Qt
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QToolBar, QLineEdit,
    QAction, QWidget, QVBoxLayout, QStyle, QTabBar, QPushButton
)
from PyQt5.QtWebEngineWidgets import QWebEngineView

# ---------------------------------------------------------------------------
# Color scheme
# ---------------------------------------------------------------------------
COLOR_BLACK = "#121212"
COLOR_BLACK_LIGHT = "#1E1E1E"
COLOR_ORANGE = "#FF8C42"
COLOR_CORAL = "#FF6F5E"
COLOR_TEXT = "#F5F5F5"

STYLESHEET = f"""
QMainWindow {{
    background-color: {COLOR_BLACK};
}}

QToolBar {{
    background-color: {COLOR_BLACK_LIGHT};
    border: none;
    padding: 6px;
    spacing: 6px;
}}

QToolBar QToolButton {{
    background-color: {COLOR_ORANGE};
    color: {COLOR_BLACK};
    border-radius: 6px;
    padding: 6px 10px;
    font-weight: bold;
}}

QToolBar QToolButton:hover {{
    background-color: {COLOR_CORAL};
    color: {COLOR_TEXT};
}}

QToolBar QToolButton:pressed {{
    background-color: #E85A4A;
}}

QLineEdit {{
    background-color: {COLOR_BLACK};
    color: {COLOR_TEXT};
    border: 2px solid {COLOR_ORANGE};
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 13px;
    selection-background-color: {COLOR_CORAL};
}}

QLineEdit:focus {{
    border: 2px solid {COLOR_CORAL};
}}

QTabWidget::pane {{
    border: none;
    background-color: {COLOR_BLACK};
}}

QTabBar {{
    background-color: {COLOR_BLACK_LIGHT};
}}

QTabBar::tab {{
    background-color: {COLOR_BLACK_LIGHT};
    color: {COLOR_TEXT};
    padding: 8px 18px;
    margin-right: 2px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    min-width: 0px;
    max-width: 240px;
}}

QTabBar::tab:selected {{
    background-color: {COLOR_ORANGE};
    color: {COLOR_BLACK};
    font-weight: bold;
}}

QTabBar::tab:hover:!selected {{
    background-color: {COLOR_CORAL};
    color: {COLOR_TEXT};
}}

QTabBar::close-button {{
    subcontrol-position: right;
}}

QStatusBar {{
    background-color: {COLOR_BLACK_LIGHT};
    color: {COLOR_ORANGE};
}}

#newTabButton {{
    background-color: {COLOR_BLACK_LIGHT};
    color: {COLOR_ORANGE};
    border: none;
    border-radius: 8px;
    font-size: 18px;
    font-weight: bold;
    min-width: 32px;
    max-width: 32px;
    min-height: 28px;
    max-height: 28px;
    margin: 2px;
}}

#newTabButton:hover {{
    background-color: {COLOR_ORANGE};
    color: {COLOR_BLACK};
}}

#newTabButton:pressed {{
    background-color: {COLOR_CORAL};
    color: {COLOR_TEXT};
}}
"""

# I'm sorry for what you are about to see 
HOME_URL = "file://" + sys.path[0] + "/blackhole.html"  # Local HTML file as home page

class BrowserTab(QWebEngineView):
    def __init__(self, url=HOME_URL):
        super().__init__()
        self.load(QUrl(url))


class AdaptiveTabBar(QTabBar):
    """Keep tabs at or below 240px, shrinking them as the tab bar fills."""

    MAX_TAB_WIDTH = 240

    def tabSizeHint(self, index):
        size = super().tabSizeHint(index)
        tab_count = max(1, self.count())
        tab_widget = self.parentWidget()
        available_width = tab_widget.width() if tab_widget else self.width()
        available_per_tab = max(1, available_width // tab_count)
        size.setWidth(min(self.MAX_TAB_WIDTH, available_per_tab))
        return size

    def minimumTabSizeHint(self, index):
        # A tab may compress below its preferred width when the row is full.
        return QSize(0, self.tabSizeHint(index).height())

    def minimumSizeHint(self):
        # Do not make the main window wider just because more tabs were added.
        return QSize(0, super().minimumSizeHint().height())


class BlackholeBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blackhole")
        self.resize(1200, 800)
        self.setStyleSheet(STYLESHEET)

        # Central tab widget
        self.tabs = QTabWidget()
        self.tabs.setTabBar(AdaptiveTabBar())
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabBar().setExpanding(False)
        self.tabs.tabBar().setUsesScrollButtons(False)
        self.tabs.tabBar().setElideMode(Qt.ElideRight)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.setCentralWidget(self.tabs)

        # "+" button sits in the corner of the tab row for an intuitive new-tab action
        self.new_tab_button = QPushButton("+")
        self.new_tab_button.setObjectName("newTabButton")
        self.new_tab_button.setCursor(Qt.PointingHandCursor)
        self.new_tab_button.setToolTip("New Tab")
        self.new_tab_button.clicked.connect(lambda: self.add_new_tab())
        self.tabs.setCornerWidget(self.new_tab_button, Qt.TopRightCorner)

        # Navigation toolbar
        nav_bar = QToolBar("Navigation")
        nav_bar.setMovable(False)
        self.addToolBar(nav_bar)

        back_btn = QAction("◀", self)
        back_btn.triggered.connect(lambda: self.current_browser().back())
        nav_bar.addAction(back_btn)

        forward_btn = QAction("▶", self)
        forward_btn.triggered.connect(lambda: self.current_browser().forward())
        nav_bar.addAction(forward_btn)

        reload_btn = QAction("⟳", self)
        reload_btn.triggered.connect(lambda: self.current_browser().reload())
        nav_bar.addAction(reload_btn)

        home_btn = QAction("⌂", self)
        home_btn.triggered.connect(self.go_home)
        nav_bar.addAction(home_btn)

        # URL bar
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        nav_bar.addWidget(self.url_bar)

        go_btn = QAction("Go", self)
        go_btn.triggered.connect(self.navigate_to_url)
        nav_bar.addAction(go_btn)

        # Start with one tab
        self.add_new_tab(HOME_URL, "New Tab")

    # -- Tab management -----------------------------------------------
    def add_new_tab(self, url=HOME_URL, label="New Tab"):
        browser = BrowserTab(url)
        index = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(index)

        browser.urlChanged.connect(lambda qurl, b=browser: self.update_url_bar(qurl, b))
        browser.loadFinished.connect(lambda _, b=browser, i=index: self.update_tab_title(b, i))
        return browser

    def close_tab(self, index):
        if self.tabs.count() < 2:
            self.close()
            return
        self.tabs.removeTab(index)

    def current_tab_changed(self, index):
        if index >= 0:
            qurl = self.current_browser().url()
            self.url_bar.setText(qurl.toString())

    def current_browser(self):
        return self.tabs.currentWidget()

    def update_tab_title(self, browser, index):
        title = browser.page().title()
        if title:
            short = (title[:15] + "…") if len(title) > 15 else title
            self.tabs.setTabText(self.tabs.indexOf(browser), short)

    # -- Navigation -----------------------------------------------------
    def navigate_to_url(self):
        text = self.url_bar.text().strip()
        if not text:
            return
        if "." in text and " " not in text:
            if not text.startswith("http://") and not text.startswith("https://"):
                text = "https://" + text
            url = QUrl(text)
        else:
            url = QUrl("https://duckduckgo.com/?q=" + text.replace(" ", "+"))
        self.current_browser().setUrl(url)

    def update_url_bar(self, qurl, browser):
        if browser == self.current_browser():
            self.url_bar.setText(qurl.toString())
            self.url_bar.setCursorPosition(0)

    def go_home(self):
        self.current_browser().setUrl(QUrl(HOME_URL))


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Blackhole")
    window = BlackholeBrowser()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
