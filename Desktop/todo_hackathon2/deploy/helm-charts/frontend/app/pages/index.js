// pages/index.js
export default function Home() {
  return (
    <div style={{
      fontFamily: 'Arial, sans-serif',
      textAlign: 'center',
      marginTop: '50px',
      backgroundColor: '#f0f8ff',
      padding: '20px',
      borderRadius: '10px'
    }}>
      <h1>Welcome to Next.js Frontend!</h1>
      <p>This is a sample Next.js application deployed using Helm charts.</p>
      <div style={{marginTop: '20px'}}>
        <h2>Deployment Status</h2>
        <p>✅ Application is running in Kubernetes cluster</p>
        <p>✅ Helm chart deployed successfully</p>
        <p>✅ 2 replicas running</p>
      </div>
    </div>
  )
}