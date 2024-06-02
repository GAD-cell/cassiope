import { useEffect, useState } from 'react'

import React from 'react'

const Main = () => {

  const [time, setTime] = useState<number>(0)

  useEffect(() => {
    fetch('/time').then(res => res.json()).then(data => {
      console.log(data)
      setTime(data.time)
    });
  }, [])

  return (
    <div className=''>
        <form action="/paper-stats" method="post" encType="multipart/form-data" className='mx-auto max-w-sm'>

          <div className='mb-4'>
            <label htmlFor='pdf'>PDF</label>
            <input type="file" name="pdf" />
          </div>

          <div className='mb-5'>
            <label htmlFor='latex_zip'>LaTeX Zipped project</label>
            <input type="file" name="latex_zip" />
          </div>

          <input type="submit" value="Upload" />
        </form>   
      <p>Time: {time}</p>
    </div>
  )
}

export default Main