# 聊天加密功能 - 快速参考

## 🔑 密钥操作

### 生成密钥
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 配置密钥
```bash
# 方法 1: 环境变量
export MESSAGE_ENCRYPTION_KEY="your-key-here"

# 方法 2: .env 文件
echo "MESSAGE_ENCRYPTION_KEY=your-key-here" >> .env

# 方法 3: settings.py
MESSAGE_ENCRYPTION_KEY = 'your-key-here'
```

---
