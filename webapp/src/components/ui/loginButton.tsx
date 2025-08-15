import { GoogleLogin } from '@react-oauth/google'
import { useSessionToken } from '../../hooks/useSessionToken'

export default function LoginButton() {
  const { saveToken } = useSessionToken()

  const handleSuccess = (response: any) => {
    const token = response?.credential
    if (!token) return

    /**
     * Here you can also implement Supabase.com authorization,
     * which is perfect for MVP projects to test your business model
     */

    saveToken(token)
    console.log('Login successful, token saved')
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
