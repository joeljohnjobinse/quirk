import { useState, useEffect, useRef } from "react"
import Editor from "@monaco-editor/react"
import axios from "axios"

export default function App() {
  const [code, setCode] = useState(`nums = [1,2,3,4]

for i in nums
    print i
end`)
  const [output, setOutput] = useState("")
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState(false)

  const handleEditorWillMount = (monaco) => {
    monaco.languages.register({ id: "quirk" })

    monaco.languages.setMonarchTokensProvider("quirk", {
      tokenizer: {
        root: [
          [/\b(function|print|return|if|else|for|while|end|import|in)\b/, "keyword"],
          [/[a-zA-Z_]\w*/, "identifier"],
          [/\d+/, "number"],
          [/".*?"/, "string"],
        ],
      },
    })
  }

  const runCode = async () => {
    setLoading(true)

    const res = await axios.post("/run", { code })

    if (res.data.error) {
      setOutput(res.data.message)

      const model = editorRef.current.getModel()

      window.monaco.editor.setModelMarkers(model, "owner", [
        {
          startLineNumber: res.data.line,
          startColumn: 1,
          endLineNumber: res.data.line,
          endColumn: 100,
          message: res.data.message,
          severity: window.monaco.MarkerSeverity.Error,
        }
      ])
    } else {
      setOutput(res.data.output)

      window.monaco.editor.setModelMarkers(
        editorRef.current.getModel(),
        "owner",
        []
      )
    }

    setLoading(false)
  }

  const editorRef = useRef(null)

  const handleEditorDidMount = (editor, monaco) => {
    editorRef.current = editor
    window.monaco = monaco
  }

  const copyOutput = () => {
    navigator.clipboard.writeText(output)
    setCopied(true)
    setTimeout(() => setCopied(false), 1200)
  }

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.ctrlKey && e.key === "Enter") runCode()
    }
    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  })

  return (
    <div className="min-h-screen bg-[#0b0f19] text-white p-10">
      <h1 className="text-3xl font-bold mb-6">⚡ Quirk Playground</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

        <div className="rounded-2xl overflow-hidden border border-white/10">
          <Editor
            height="500px"
            theme="vs-dark"
            defaultLanguage="quirk"
            beforeMount={handleEditorWillMount}
            onMount={handleEditorDidMount}
            value={code}
            onChange={(v) => setCode(v)}
          />
        </div>

        <div className="rounded-2xl bg-black/40 border border-white/10 p-6 flex flex-col">
          <div className="flex justify-between mb-4">
            <span>Terminal</span>
            <button
              onClick={copyOutput}
              className="text-sm bg-white/10 px-3 py-1 rounded"
            >
              {copied ? "Copied!" : "Copy"}
            </button>
          </div>

          <pre className="flex-1 text-green-400 font-mono">
            {output || "Run your code to see output"}
          </pre>
        </div>
      </div>

      <button
        onClick={runCode}
        disabled={loading}
        className="mt-8 px-10 py-3 bg-indigo-600 hover:bg-indigo-500 rounded-xl"
      >
        {loading ? "Running..." : "Run Code (Ctrl + Enter)"}
      </button>
    </div>
  )
}
