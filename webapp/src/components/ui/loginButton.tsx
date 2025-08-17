import { GoogleLogin } from '@react-oauth/google'
import { useAuth } from '../../hooks/useAuth'
import { api } from "../../lib/api"

export default function LoginButton() {
  const { saveToken } = useAuth()

  const handleSuccess = async (response: { credential?: string }) => {
    const token = response?.credential
    if (!token) {
      console.error('No credential received from Google')
      return
    }

    try {
      const authResponse = await api.addUserToDataBase({ credential: token })
      console.log('Auth successful:', authResponse)
      saveToken(authResponse.token)
    } catch (error) {
      console.error('Authentication failed:', error)
    }
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
