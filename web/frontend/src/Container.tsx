import React from 'react'

const Container = (props:any) => {
  return (
    <div className='mx-auto px-12 py-6'>
        {props.children}
    </div>
  )
}

export default Container