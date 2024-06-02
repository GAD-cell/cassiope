import React from 'react'

const Container = (props:any) => {
  return (
    <div className='mx-auto py-6 max-w-lg'>
        {props.children}
    </div>
  )
}

export default Container