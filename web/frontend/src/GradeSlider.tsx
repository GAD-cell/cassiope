import React from 'react'
import ReactSlider from 'react-slider'

const GradeSlider = (props:any) => {

  const property = props.property
  const value = props.value

  // If value is not a number, return null
  if (typeof value !== 'number') return null

  const min = 0
  const max = 100

  // Range of good values
  const min_good = 20 + Math.random() * (25)
  const max_good = 50 + Math.random() * (25)

  // Generate a table of good values : one by one, from min_good to max_good
  const good_marks = Array.from({ length: max_good - min_good + 1 }, (_, i) => min_good + i)

  /*
  This component displays the 'value' of a property in a slider. The slider has a range from 0 to 100.
  The slider has no effect. It is only for display purposes.
  It should display whether the value is in the 'good' range or not.
  */

  const isGood = value >= min_good && value <= max_good

  return (
    <div>
      <ReactSlider
        className='w-64 h-4'
        thumbClassName={`w-3 h-3 mt-0.5 ${isGood ? "bg-green-600" : "bg-gray-500"} rounded-full`}
        trackClassName='h-4 bg-gray-100 rounded-full border'
        defaultValue={value}
        min={min}
        max={max}
        marks={good_marks}
        markClassName={`h-4 bg-green-200 w-1`}
        disabled
      />
    </div>
  )
}

export default GradeSlider