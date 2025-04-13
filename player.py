import os
from PySide6.QtCore import QObject, QSettings, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

class TBPlayer(QObject):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("TomatoBar", "TomatoBar")
        
        # 创建音频播放器
        self.windupSound = self._createAudioPlayer("windup.wav")
        self.dingSound = self._createAudioPlayer("ding.wav")
        self.tickingSound = self._createAudioPlayer("ticking.wav")
        
        # 加载音量设置
        self.windupVolume = self.settings.value("windupVolume", 1.0, float)
        self.dingVolume = self.settings.value("dingVolume", 1.0, float)
        self.tickingVolume = self.settings.value("tickingVolume", 1.0, float)
        
        # 设置音量
        self._setVolume(self.windupSound, self.windupVolume)
        self._setVolume(self.dingSound, self.dingVolume)
        self._setVolume(self.tickingSound, self.tickingVolume)
    
    def _createAudioPlayer(self, filename):
        """创建音频播放器"""
        # 检查文件是否存在
        for path in [
            f"Assets/{os.path.splitext(filename)[0]}.dataset/{filename}",  # 原版结构
            f"Assets/{filename}",  # 备用位置
            f"sounds/{filename}"  # 备用位置
        ]:
            if os.path.exists(path):
                player = QMediaPlayer()
                audio_output = QAudioOutput()
                player.setAudioOutput(audio_output)
                player.setSource(QUrl.fromLocalFile(os.path.abspath(path)))
                return {"player": player, "audio": audio_output}
        
        print(f"警告: 找不到音频文件 {filename}")
        return None
    
    def _setVolume(self, sound, volume):
        """设置音频播放器的音量"""
        if sound:
            sound["audio"].setVolume(volume)
    
    def setWindupVolume(self, volume):
        """设置发条声音量"""
        self.windupVolume = volume
        self.settings.setValue("windupVolume", volume)
        self._setVolume(self.windupSound, volume)
    
    def setDingVolume(self, volume):
        """设置叮声音量"""
        self.dingVolume = volume
        self.settings.setValue("dingVolume", volume)
        self._setVolume(self.dingSound, volume)
    
    def setTickingVolume(self, volume):
        """设置滴答声音量"""
        self.tickingVolume = volume
        self.settings.setValue("tickingVolume", volume)
        self._setVolume(self.tickingSound, volume)
    
    def playWindup(self):
        """播放发条声"""
        if self.windupSound and self.windupVolume > 0:
            self.windupSound["player"].setPosition(0)
            self.windupSound["player"].play()
    
    def playDing(self):
        """播放叮声"""
        if self.dingSound and self.dingVolume > 0:
            self.dingSound["player"].setPosition(0)
            self.dingSound["player"].play()
    
    def startTicking(self):
        """开始播放滴答声"""
        if self.tickingSound and self.tickingVolume > 0:
            self.tickingSound["player"].setLoops(QMediaPlayer.Infinite)
            self.tickingSound["player"].play()
    
    def stopTicking(self):
        """停止播放滴答声"""
        if self.tickingSound:
            self.tickingSound["player"].stop()
            # 确保停止后重置位置，避免下次播放从中间开始
            self.tickingSound["player"].setPosition(0)
