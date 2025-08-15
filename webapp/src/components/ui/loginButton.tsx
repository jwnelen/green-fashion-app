import { GoogleLogin } from '@react-oauth/google'
import { useAuth } from '../../contexts/AuthContext'

export default function LoginButton() {
  const { saveToken } = useAuth()

  const handleSuccess = (response: any) => {
    const token = response?.credential
    if (!token) {
      console.error('No credential received from Google')
      return
    }

    /**
     * Here you can also implement Supabase.com authorization,
     * which is perfect for MVP projects to test your business model
     */

    saveToken(token)
  }

  const handleError = () => {
    console.error('Login failed')
  }

  return (
    <>
      <GoogleLogin onSuccess={handleSuccess} onError={handleError} />
    </>
  )
}
