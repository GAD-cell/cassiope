import React from 'react'
import ReactSlider from 'react-slider'

const GradeSlider = (props:any) => {

  // Bounds for the slider
  // "property" : [min, max, min_good, max_good]
  const BOUNDS : {[key: string]: number[]} = {
    "abstract_length":    [0, 400, 150, 250],
    "acronym_presence":   [],
    "authors":            [1, 20, 2, 5],
    "content_references": [0, 500, 35, 95],
    "equations":          [0, 400, 25, 105],
    "figures":            [0, 150, 5, 35],
    "font":               [],
    "pages":              [3, 60, 15, 25],
    "paragraphs":         [0, 100, 5, 15],
    "sections":           [0, 20, 5, 9],
    "subsections":        [0, 60, 4, 12],
    "subsubsections":     [0, 50, 20, 30],
    "tables":             [0, 80, 3, 10],
    "title_length":       [0, 200, 20, 50],
    "words":              [0, 30000, 6000, 13000]
  }

  const property = props.property
  const value = props.value

  // If value is not a number, return null
  if (typeof value !== 'number') return null

  const [min, max, min_good, max_good] = BOUNDS[property] ?? [0, 1000, 250, 750]

  // Generate a table of good values : one by one, from min_good to max_good
  const good_marks = () => Array.from({ length: max_good - min_good + 1 }, (_, i) => min_good + i)

  /*
  This component displays the 'value' of a property in a slider. The slider has a range from 0 to 100.
  The slider has no effect. It is only for display purposes.
  It should display whether the value is in the 'good' range or not.
  */

  const isGood = value >= min_good && value <= max_good

  return (
    <div>
      <ReactSlider
        className='w-52 h-4'
        thumbClassName={`w-4 h-4 border-4 ${isGood ? "bg-green-600 border-green-300" : "bg-gray-500"} rounded-full`}
        trackClassName='h-2 mt-1 bg-gray-200 rounded-full'
        defaultValue={value}
        min={min}
        max={max}
        marks={good_marks()}
        markClassName={`h-2 mt-1 bg-green-300 w-3`}
        disabled
      />
    </div>
  )
}

export default GradeSlider