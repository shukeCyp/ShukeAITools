# -*- coding: utf-8 -*-
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import (Dialog, BodyLabel, PrimaryPushButton, PushButton,
                           FluentIcon as FIF, InfoBar, InfoBarPosition)
from app.utils.logger import log


class QQGroupDialog(Dialog):
    """QQ群提示对话框"""

    def __init__(self, parent=None):
        super().__init__("", "", parent)
        self.setFixedWidth(500)
        self.setFixedHeight(280)
        self.titleLabel.setVisible(False)
        self._initUI()

    def _initUI(self):
        content = QWidget(self)
        layout = QVBoxLayout(content)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(20)

        # 标题
        title_label = BodyLabel("📢 重要通知", content)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #0078d4;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # 通知内容
        message_label = BodyLabel(
            "因微信群过多导致通知较为麻烦，现在开通了QQ群聊，\n"
            "可点击下方按钮加入VideoRobot交流群！\n\n"
            "在群里可以：\n"
            "• 获取最新版本更新通知\n"
            "• 交流使用经验和技巧\n"
            "• 反馈问题和建议\n"
            "• 获得技术支持",
            content
        )
        message_label.setStyleSheet("font-size: 14px; line-height: 1.6;")
        message_label.setAlignment(Qt.AlignLeft)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)

        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        # 加入QQ群按钮
        self.joinGroupBtn = PrimaryPushButton(FIF.PEOPLE, "加入QQ群", content)
        self.joinGroupBtn.clicked.connect(self.onJoinGroup)
        button_layout.addWidget(self.joinGroupBtn)

        # 稍后提醒按钮
        self.laterBtn = PushButton("稍后提醒", content)
        self.laterBtn.clicked.connect(self.reject)
        button_layout.addWidget(self.laterBtn)

        # 不再提醒按钮
        self.neverBtn = PushButton("不再提醒", content)
        self.neverBtn.clicked.connect(self.onNeverRemind)
        button_layout.addWidget(self.neverBtn)

        layout.addLayout(button_layout)

        self.textLayout.addWidget(content)

        # 隐藏默认按钮
        self.yesButton.setVisible(False)
        self.cancelButton.setVisible(False)

    def onJoinGroup(self):
        """加入QQ群"""
        try:
            qq_group_url = "https://qm.qq.com/cgi-bin/qm/qr?k=ZzyA2XluI6GOSf6ohJI2fl3UmLKk4xtt&jump_from=webapi&authKey=RGoOt0SCfCT274RdmkJAV4oZbn0oQBUhbzfEKSRmPljYZaF4m7/d6Audcj1FFKnl"

            # 使用系统默认浏览器打开链接
            success = QDesktopServices.openUrl(QUrl(qq_group_url))

            if success:
                log.info("已打开QQ群链接")
                InfoBar.success(
                    title="成功",
                    content="已在浏览器中打开QQ群链接",
                    parent=self,
                    duration=2000,
                    position=InfoBarPosition.TOP
                )
                # 设置不再提醒并关闭对话框
                self._setNeverRemind()
                self.accept()
            else:
                log.error("打开QQ群链接失败")
                InfoBar.error(
                    title="失败",
                    content="无法打开链接，请手动复制链接到浏览器",
                    parent=self,
                    position=InfoBarPosition.TOP
                )

        except Exception as e:
            log.error(f"打开QQ群链接异常: {e}")
            InfoBar.error(
                title="错误",
                content=f"打开链接时出错: {str(e)}",
                parent=self,
                position=InfoBarPosition.TOP
            )

    def onNeverRemind(self):
        """不再提醒"""
        self._setNeverRemind()
        self.reject()

    def _setNeverRemind(self):
        """设置不再提醒标志"""
        try:
            from app.utils.config_manager import get_config_manager
            config_manager = get_config_manager()
            config_manager.set("qq_group_dialog_shown", True)
            log.info("已设置QQ群对话框不再提醒")
        except Exception as e:
            log.error(f"设置不再提醒失败: {e}")

    @staticmethod
    def should_show():
        """检查是否应该显示QQ群对话框"""
        try:
            from app.utils.config_manager import get_config_manager
            config_manager = get_config_manager()
            shown = config_manager.get("qq_group_dialog_shown", False)
            return not shown
        except Exception as e:
            log.error(f"检查QQ群对话框显示状态失败: {e}")
            return True  # 出错时默认显示