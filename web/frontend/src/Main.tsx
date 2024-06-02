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
      <h1>Main</h1>

      <p>Time: {time}</p>
    </div>
  )
}

export default Main