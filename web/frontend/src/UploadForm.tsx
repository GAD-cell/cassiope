import React from 'react'
import { useMemo } from 'react'

const UploadForm = (props: any) => {

    const pdf = props.pdf
    const latexZip = props.latexZip
    const setPdf = props.setPdf
    const setLatexZip = props.setLatexZip
    const handleSubmit = props.handleSubmit

    const canUpload = useMemo(() => {
        const pdf_is_a_pdf_file = pdf && pdf.name.endsWith('.pdf');
        const latex_zip_is_a_zip_file = latexZip && latexZip.name.endsWith('.zip');
        return pdf_is_a_pdf_file && latex_zip_is_a_zip_file

    }, [pdf, latexZip])

    console.log(pdf, latexZip, canUpload)

    return (
        <form method="post" encType="multipart/form-data" className='mx-auto max-w-lg'>

            <div className='mb-4'>
                <label htmlFor='pdf' className="block text-md font-semibold">PDF</label>
                <label htmlFor='pdf' className="block mb-2 text-sm text-gray-500">Your paper in .pdf format</label>
                <input type="file" name="pdf"
                    onChange={(e) => { setPdf(e.target.files![0]) }} />
            </div>

            <div className='mb-4'>
                <label htmlFor='latex_zip' className="block text-md font-semibold">LaTeX</label>
                <label htmlFor='latex_zip' className="block mb-2 text-sm text-gray-500">The entire LaTeX projet for this paper, in a .zip archive</label>
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