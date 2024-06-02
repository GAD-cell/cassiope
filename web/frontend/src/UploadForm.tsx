import React from 'react'
import { useMemo } from 'react'

const UploadForm = (props: any) => {

    const pdf = props.pdf
    const latexZip = props.latexZip
    const setPdf = props.setPdf
    const setLatexZip = props.setLatexZip
    const handleSubmit = props.handleSubmit

    const canUpload = useMemo(() => {
        return pdf && latexZip
    }, [pdf, latexZip])

    console.log(pdf, latexZip, canUpload)

    return (
        <form method="post" encType="multipart/form-data" className='mx-auto max-w-lg'>

            <div className='mb-4'>
                <label htmlFor='pdf' className="block mb-2 text-sm">PDF</label>
                <input type="file" name="pdf"
                    onChange={(e) => { setPdf(e.target.files![0]) }} />
            </div>

            <div className='mb-4'>
                <label htmlFor='latex_zip' className="block mb-2 text-sm">LaTeX Zipped project</label>
                <input type="file" name="latex_zip"
                    onChange={(e) => { setLatexZip(e.target.files![0]) }}
                />
            </div>

            <button
                onClick={handleSubmit}
                disabled={!canUpload}
                className={`text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 disabled:opacity-25 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full px-5 py-2.5 text-center`}>
                    Upload
                </button>
        </form>
    )
}

export default UploadForm