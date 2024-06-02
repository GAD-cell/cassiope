import { useEffect, useState } from 'react'

import StatsDisplay from './StatsDisplay'
import UploadForm from './UploadForm'

const Main = () => {

  const [time, setTime] = useState<number>(0)
  const [pdf, setPdf] = useState<File>()
  const [latexZip, setLatexZip] = useState<File>()
  const [paperStats, setPaperStats] = useState<any>()

  useEffect(() => {
    fetch('/time').then(res => res.json()).then(data => {
      setTime(data.time)
    });
  }, [])

  const handleSubmit = (e: any) => {
    e.preventDefault()
    const formData = new FormData()
    formData.append('pdf', pdf!)
    formData.append('latex_zip', latexZip!)
    fetch('/paper-stats', {
      method: 'POST',
      body: formData
    }).then(res => res.json()).then(data => {
      console.log(data)
      setPaperStats(data)
    });
  }

  return (
    <>
        <UploadForm pdf={pdf} setPdf={setPdf} setLatexZip={setLatexZip} latexZip={latexZip} handleSubmit={handleSubmit} />
        <StatsDisplay {...paperStats} />
      <p className='mt-4 text-xs text-gray-400'>Time: {time}</p>
    </>
  )
}

export default Main