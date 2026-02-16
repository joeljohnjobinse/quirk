const express = require("express")
const cors = require("cors")
const { exec } = require("child_process")
const fs = require("fs")
const path = require("path")

const app = express()

app.use(cors())
app.use(express.json())

// --------------------------------------------------
// RUN CODE API
// --------------------------------------------------

app.post("/run", (req, res) => {
  const code = req.body.code || ""

  const projectRoot = path.join(__dirname, "..")
  const filePath = path.join(projectRoot, "temp.qk")

  try {
    fs.writeFileSync(filePath, code)
  } catch (err) {
    return res.json({
      error: true,
      message: "Failed to write temporary file.",
    })
  }

  exec(
    `python -m quirk.cli temp.qk`,
    { timeout: 5000, cwd: projectRoot },
    (err, stdout, stderr) => {

      const raw = (stdout + stderr).trim()

      // If nothing returned
      if (!raw) {
        return res.json({ output: "" })
      }

      // Match "(line X)"
      const match = raw.match(/\(line\s+(\d+)\)/i)

      if (match) {
        return res.json({
          error: true,
          message: raw,
          line: parseInt(match[1], 10)
        })
      }

      return res.json({
        output: raw
      })
    }
  )
})


// --------------------------------------------------
// SERVE REACT BUILD (PRODUCTION)
// --------------------------------------------------

const clientBuildPath = path.join(__dirname, "../client/build")

app.use(express.static(clientBuildPath))

app.get(/.*/, (req, res) => {
  res.sendFile(path.join(clientBuildPath, "index.html"))
})


// --------------------------------------------------
// START SERVER
// --------------------------------------------------

const PORT = process.env.PORT || 5000

app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`)
})
