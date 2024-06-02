import React from 'react'

const Container = (props:any) => {
  return (<div className='bg-gray-50 h-screen'>
    <div className='mx-auto py-6 max-w-lg'>
        {props.children}
    </div>
  </div>)
}

export default Container