import { useEffect, useState } from 'react'

import { PresentationChartBarIcon } from '@heroicons/react/24/solid'
import StatsDisplay from './StatsDisplay'
import UploadForm from './UploadForm'

const Main = () => {

  const [time, setTime] = useState<number>(0)
  const [pdf, setPdf] = useState<File>()
  const [latexZip, setLatexZip] = useState<File>()
  const [paperStats, setPaperStats] = useState<any>()
  const [loading, setLoading] = useState<boolean>(false)

  useEffect(() => {
    fetch('/time').then(res => res.json()).then(data => {
      setTime(data.time)
    });
  }, [])

  const handleSubmit = (e: any) => {
    e.preventDefault()
    setLoading(true)
    const formData = new FormData()
    formData.append('pdf', pdf!)
    formData.append('latex_zip', latexZip!)
    fetch('/paper-stats', {
      method: 'POST',
      body: formData
    }).then(res => res.json()).then(data => {
      console.log(data)
      setPaperStats(data)
    }).finally(() => {
      setLoading(false)
    })
  }

  const Status = () => {
    return time === 0 || time === undefined ? <p className='text-xs text-red-500'>The server is not responding</p> : <p className='text-xs text-gray-400'>The server is live :)</p>
  }

  return (
    <div className='bg-white p-4 rounded-xl'>
      <h1 className='text-xl font-semibold flex items-center gap-2 mb-2 bg-blue-50 px-3 py-2 rounded-xl border-blue-200 border-2 text-blue-700 shadow-sm shadow-blue-5°'>
        <PresentationChartBarIcon className='w-5 h-5' />
        Paper Stats
      </h1>
      
      <p className='text-sm text-blue-500 mb-4 px-1'>Feed this tool your paper and learn how you can make it more likely to be published, based on experience.</p>

      <UploadForm pdf={pdf} setPdf={setPdf} setLatexZip={setLatexZip} latexZip={latexZip} handleSubmit={handleSubmit} />
      {loading ? <p className='text-center mt-4'>Loading...</p> :
        <>
          <h2 className='text-lg font-semibold mt-4'>{pdf?.name.replace(".pdf", "")}</h2>
          <StatsDisplay {...paperStats} />
        </>}
      <Status />
    </div>
  )
}

export default Main