import json

from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QDialog,
    QListWidget,
    QLineEdit,
    QSlider,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox
)


class SettingsDialog(QDialog):

    def __init__(self, settings):
        super().__init__()

        self.settings = settings

        self.setWindowTitle("プロファイル設定")
        self.resize(500, 400)

        self.build_ui()

        self.load_profiles()

    def build_ui(self):

        root = QHBoxLayout()

        # 左側
        self.profile_list = QListWidget()
        root.addWidget(self.profile_list)

        # 右側
        right = QVBoxLayout()

        right.addWidget(QLabel("名前"))

        self.name_edit = QLineEdit()
        right.addWidget(self.name_edit)

        right.addWidget(QLabel("速度"))

        self.speed_slider = QSlider(
            Qt.Orientation.Horizontal
        )

        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(20)

        right.addWidget(self.speed_slider)

        self.speed_label = QLabel("1")
        right.addWidget(self.speed_label)

        right.addWidget(QLabel("スクロール行数"))

        self.scroll_slider = QSlider(
            Qt.Orientation.Horizontal
        )

        self.scroll_slider.setMinimum(1)
        self.scroll_slider.setMaximum(20)

        right.addWidget(self.scroll_slider)

        self.scroll_label = QLabel("3")
        right.addWidget(self.scroll_label)


        self.speed_slider.valueChanged.connect(
            lambda value:
            self.speed_label.setText(str(value))
        )

        self.scroll_slider.valueChanged.connect(
            lambda value:
            self.scroll_label.setText(str(value))
        )

        # ボタン
        button_layout = QHBoxLayout()

        self.add_button = QPushButton("追加")
        self.save_button = QPushButton("保存")
        self.delete_button = QPushButton("削除")
        self.close_button = QPushButton("閉じる")

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.close_button)

        right.addLayout(button_layout)

        root.addLayout(right)

        self.setLayout(root)

        # イベント
        self.profile_list.currentRowChanged.connect(
            self.profile_selected
        )

        self.add_button.clicked.connect(
            self.add_profile
        )

        self.save_button.clicked.connect(
            self.save_profile
        )

        self.delete_button.clicked.connect(
            self.delete_profile
        )

        self.close_button.clicked.connect(
            self.accept
        )

    def load_profiles(self):

        self.profile_list.clear()

        for profile in self.settings["profiles"]:
            self.profile_list.addItem(
                profile["name"]
            )

        if self.profile_list.count() > 0:
            self.profile_list.setCurrentRow(0)

    def profile_selected(self, row):
        
        if row < 0:
            return

        profile = self.settings["profiles"][row]

        self.name_edit.setText(
            profile["name"]
        )

        self.speed_slider.setValue(
            profile["speed"]
        )

        if "scroll_lines" in profile:
            self.scroll_slider.setValue(
                profile["scroll_lines"]
            )
        else:
            self.scroll_slider.setValue(5)


    def add_profile(self):

        profile = {
            "name": "新しいプロファイル",
            "speed": 10,
            "scroll_lines": 5
        }

        self.settings["profiles"].append(
            profile
        )

        self.load_profiles()

        self.profile_list.setCurrentRow(
            len(self.settings["profiles"]) - 1
        )

    def save_profile(self):

        row = self.profile_list.currentRow()

        if row < 0:
            return

        name = self.name_edit.text().strip()

        if not name:

            QMessageBox.warning(
                self,
                "エラー",
                "名前を入力してください"
            )

            return

        self.settings["profiles"][row]["name"] = name
        self.settings["profiles"][row]["speed"] = (
            self.speed_slider.value()
        )
        self.settings["profiles"][row]["scroll_lines"] = (
            self.scroll_slider.value()
        )

        with open(
            "settings.json",
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                self.settings,
                f,
                ensure_ascii=False,
                indent=2
            )

        QMessageBox.information(
            self,
            "保存",
            "保存しました"
        )

    def delete_profile(self):

        row = self.profile_list.currentRow()

        if row < 0:
            return

        reply = QMessageBox.question(
            self,
            "削除確認",
            "削除しますか？"
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        del self.settings["profiles"][row]

        with open(
            "settings.json",
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                self.settings,
                f,
                ensure_ascii=False,
                indent=2
            )

        self.load_profiles()