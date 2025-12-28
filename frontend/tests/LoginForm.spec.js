import { describe,it,expect, beforeEach, vi } from 'vitest'
import LoginForm from "@/pages/Login.vue"
import router from "@/router"
import ElementPlus from 'element-plus'
import { render, fireEvent, screen,waitFor } from "@testing-library/vue"


const { mockLogin } = vi.hoisted(() => ({
    mockLogin: vi.fn().mockResolvedValue({
      success: true,
      token: 'test-token'
    })
  }))
  
  vi.mock('@/store/user', () => {
    return {
      useUserStore: vi.fn(() => ({
        loginUser: mockLogin
      }))
    }
  })
describe('登录组件',()=>{
    beforeEach(()=>{
        router.push('/login');
        mockLogin.mockClear()
    })
    it("应该渲染表单",()=>{
        render(LoginForm, {
            global: {
              plugins: [ElementPlus] 
            }
          })
        expect(screen.getByTestId('identity-select')).toBeTruthy();
        expect(screen.getByPlaceholderText("请输入学号/教工号")).toBeTruthy();
        expect(screen.getByPlaceholderText('请输入密码')).toBeTruthy();
        expect(screen.getByRole('button', { name: /登录/ })).toBeTruthy();
    })
    it("应该显示表单验证错误",async()=>{
        render(LoginForm, {
            global: {
              plugins: [ElementPlus] 
            }
          })

        const submitButton = screen.getByRole('button', { name: /登录/ });
        fireEvent.click(submitButton);
        expect(screen.getByTestId('identity-select')).toBeTruthy();
        expect(screen.getByPlaceholderText("请输入学号/教工号")).toBeTruthy();
        expect(screen.getByPlaceholderText('请输入密码')).toBeTruthy();
    })
    it('登录表单的验证', async () => {    
        render(LoginForm, {
          global: {
            plugins: [router, ElementPlus]
          }
        })
    
        // 选择身份：学生
        const studentRadio = screen.getByRole('radio', { name: /学生/i })
        await fireEvent.click(studentRadio)
    
        // 输入账号
        const accountInput = screen.getByPlaceholderText('请输入学号/教工号')
        await fireEvent.update(accountInput, 'test-account')
    
        // 输入密码
        const passwordInput = screen.getByPlaceholderText('请输入密码')
        await fireEvent.update(passwordInput, '111111')
    
        // 点击登录按钮
        const loginButton = screen.getByRole('button', { name: '登录' })
        await fireEvent.click(loginButton)
    
        // ✅ 等待异步操作完成
        await waitFor(() => {
          expect(mockLogin).toHaveBeenCalledTimes(1)
        })
    
        // ✅ 验证调用参数
        expect(mockLogin).toHaveBeenCalledWith({
          identity: 0,
          account: 'test-account',
          password: '111111'
        })

    })  
})


