# 聊天内容加密功能文档

## 概述

本文档介绍了聊天消息的加密功能实现。该功能确保消息内容在数据库中以加密形式存储，增强用户隐私和数据安全。

## 加密方案

### 算法选择
- **算法**: Fernet (对称加密)
- **基础**: AES-128 加密 + HMAC 认证
- **安全性**: 银行级别的安全保证

### 加密流程

```
用户发送消息
    ↓
后端接收消息内容
    ↓
使用 Fernet 加密消息
    ↓
存储加密后的内容到数据库
    ↓
用户获取消息列表
    ↓
后端从数据库查询加密消息
    ↓
使用 Fernet 解密消息
    ↓
返回解密后的消息给前端
    ↓
用户看到明文消息
```

## 实现细节

### 1. 后端实现 (`backend/api/views/conversation.py`)

#### MessageEncryptor 类
```python
class MessageEncryptor:
    def encrypt(self, plaintext: str) -> str:
        """加密消息内容"""
        
    def decrypt(self, ciphertext: str) -> str:
        """解密消息内容"""
```

#### 集成点

**发送消息 (`send_message` 函数)**
- 接收用户输入的消息内容
- 使用 `encryptor.encrypt()` 加密
- 存储加密后的内容到数据库
- 自动回复消息也会被加密

```python
# 加密消息内容
encrypted_content = encryptor.encrypt(content)

# 存储加密内容
Message.objects.create(
    conversation=conversation,
    sender=sender,
    content_type=content_type,
    content=encrypted_content,  # 存储加密内容
    ...
)
```

**获取消息列表 (`list_messages` 函数)**
- 从数据库查询消息
- 使用 `encryptor.decrypt()` 解密
- 返回解密后的明文给前端

```python
# 返回前解密
'content': encryptor.decrypt(m.content),
```

### 2. 密钥管理

#### 密钥存储位置（优先级）
1. Django settings 中的 `MESSAGE_ENCRYPTION_KEY`
2. 环境变量 `MESSAGE_ENCRYPTION_KEY`

#### 配置方法

**方法一：在 `settings.py` 中设置**
```python
MESSAGE_ENCRYPTION_KEY = 'your-fernet-key-here'
```

**方法二：使用环境变量（推荐）**
```bash
# 在 .env 文件中
MESSAGE_ENCRYPTION_KEY=your-fernet-key-here

# 或在系统环境变量中设置
export MESSAGE_ENCRYPTION_KEY=your-fernet-key-here
```

#### 生成密钥
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

示例输出：
```
miHYtq32TcZ5qDXdmrketEQdvuQLdpxkby9Zmun6ens=
```

### 3. 数据库变化

**无需修改现有数据库结构**

消息内容在数据库中以加密形式存储（字符串形式），格式如：
```
gAAAAAB...（加密后的长文本）
```

### 4. 前端集成

**无需修改前端代码**

前端继续使用现有的消息发送和接收逻辑：
- 发送消息：后端自动加密
- 接收消息：后端自动解密后返回

## 安全特性

### ✓ 已实现
1. **存储加密**: 消息在数据库中以加密形式存储
2. **完整性验证**: Fernet 包含 HMAC 认证
3. **时间戳**: 加密消息包含时间戳，防止重放攻击
4. **向后兼容**: 解密失败时返回原文本（支持未加密的旧数据）

### ⚠ 限制
1. **传输层**: 仅依赖 HTTPS 保护（建议在生产环境中使用 HTTPS）
2. **密钥管理**: 使用全局密钥（所有用户共享）
   - 适用于内部协作平台
   - 可升级为每对话/每用户密钥
3. **服务器安全**: 消息在服务器内存中可见（后端处理时）

## 测试

运行测试脚本验证加密功能：

```bash
cd backend
python test_encryption.py
```

预期输出：
```
✓ 加密器初始化成功
✓ 所有测试通过！
```

## 性能影响

- 加密/解密开销：每条消息约 1-5ms
- 对于一般应用不构成性能问题
- 大规模消息应用可考虑异步加密处理

## 部署清单

- [ ] 生成安全的 Fernet 密钥
- [ ] 配置 `MESSAGE_ENCRYPTION_KEY` 环境变量
- [ ] 在 `settings.py` 中验证密钥配置
- [ ] 运行 `test_encryption.py` 验证功能
- [ ] 测试消息发送/接收流程
- [ ] 验证消息在数据库中已加密
- [ ] 配置备份策略（丢失密钥将无法恢复数据）

## 故障排除

### 问题 1: "未设置MESSAGE_ENCRYPTION_KEY"
**原因**: 环境变量或 settings 未配置  
**解决**: 按照上述密钥管理部分配置密钥

### 问题 2: "加密密钥格式不正确"
**原因**: 密钥格式无效  
**解决**: 使用上述命令生成新的 Fernet 密钥

### 问题 3: 消息显示为加密文本
**原因**: 前端收到未解密的内容（不应发生）  
**解决**: 检查后端 `list_messages` 函数是否调用了 `decrypt()`

## 未来改进

1. **每对话加密密钥**: 为每个会话生成独立密钥，增强隐私
2. **端到端加密**: 前端加密，后端无法访问明文
3. **密钥轮转**: 定期轮转加密密钥
4. **加密审计日志**: 记录加密/解密操作
5. **性能优化**: 缓存解密结果

## 参考资源

- [Cryptography 库文档](https://cryptography.io/en/latest/fernet/)
- [Fernet 规范](https://github.com/fernet/spec/blob/master/Spec.md)
- [Django 安全最佳实践](https://docs.djangoproject.com/en/4.2/topics/security/)
