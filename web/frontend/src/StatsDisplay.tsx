import React from 'react'

const StatsDisplay = (props: any) => {

    return Object.keys(props).length > 0 ? (
        <table className="w-full text-sm my-2 mt-4">
            <tbody>
                {Object.keys(props).map((key) => (
                    <tr key={key} className='border hover:bg-gray-50'>
                        <th className='text-left bg-gray-50 px-4 py-2 font-medium text capitalize'>{key.replace("_", " ")}</th>
                        <td className={`font-mono text-xs px-4 py-2 ${props[key] ? 'text-gray-900' : 'text-gray-400'}`}>{props[key] ? props[key] : 0}</td>
                    </tr>
                ))}
            </tbody>
        </table>
    ) : null;
}

export default StatsDisplay