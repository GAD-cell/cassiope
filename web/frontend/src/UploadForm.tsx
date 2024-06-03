import React from 'react'
import { useMemo } from 'react'

const UploadForm = (props: any) => {

    const pdf = props.pdf
    const latexZip = props.latexZip
    const setPdf = props.setPdf
    const setLatexZip = props.setLatexZip
    const handleSubmit = props.handleSubmit

    const EXAMPLES = [
        "attention_is_all_you_need",
    ]

    const toTitleCase = (str: string) => {
        return str.replace(/\w\S*/g, function (txt: string) { return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase(); });
    }

    const canUpload = useMemo(() => {
        const pdf_is_a_pdf_file = pdf && pdf.name.endsWith('.pdf');
        const latex_zip_is_a_zip_file = latexZip && latexZip.name.endsWith('.zip');
        return pdf_is_a_pdf_file && latex_zip_is_a_zip_file
    }, [pdf, latexZip])

    const pickExample = (example: string) => {
        const example_path = `examples/${example}`

        fetch(`${example_path}/${example}.pdf`)
            .then(response => response.blob())
            .then(blob => {
                setPdf(new File([blob], `${example}.pdf`))
            })

        fetch(`${example_path}/${example}.zip`)
            .then(response => response.blob())
            .then(blob => {
                setLatexZip(new File([blob], `${example}.zip`))
            })
    }

    const ExamplesDropdown = () => {
        return (
            <div className='mb-4'>
                <label htmlFor='example' className="block text-md font-semibold">Example</label>
                <label htmlFor='example' className="block mb-2 text-sm text-gray-500">Pick an example to upload</label>
                <select
                    onChange={(e) => pickExample(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm">
                    <option value="">Select an example</option>
                    {EXAMPLES.map((example) => <option key={example} value={example}>{toTitleCase(example.replaceAll("_", " "))}</option>)}
                </select>
            </div>
        )
    }

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
            
            <div className='text-center mb-7'>
                <label className="absolute text-md font-semibold  z-10 bg-white px-2 text-gray-400 ml-[-24px]">OR</label>
                <hr className='relative z-0 top-3 border-gray-300' />
            </div>

            <ExamplesDropdown />

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