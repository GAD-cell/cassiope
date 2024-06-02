import GradeSlider from './GradeSlider';
import React from 'react'

const StatsDisplay = (props: any) => {

    return Object.keys(props).length > 0 ? (
        <table className="text-sm my-2 mt-2">
            <tbody>
                {Object.keys(props).map((key) => (
                    <tr key={key} className='hover:bg-gray-50 divide-y divide-gray-50'>
                        <th className='text-left w-fit bg-gray-50 px-4 py-2 font-medium capitalize'>{key.replace("_", " ")}</th>
                        <td className={`font-mono text-xs px-4 py-2 ${props[key] ? 'text-gray-900' : 'text-gray-400'}`}>{props[key] ? props[key] : 0}</td>
                        <td className='px-4 py-2'>
                            <GradeSlider property={key} value={props[key]} />
                        </td>
                    </tr>
                ))}
            </tbody>
        </table>
    ) : null;
}

export default StatsDisplay