const express = require("express")
const cors = require("cors")
const { exec } = require("child_process")
const fs = require("fs")
const path = require("path")

const app = express()
app.use(cors())
app.use(express.json())

const PORT = process.env.PORT || 5000

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`)
})


app.post("/run", (req, res) => {
  const code = req.body.code

  const projectRoot = path.join(__dirname, "..")
  const filePath = path.join(projectRoot, "temp.qk")

  fs.writeFileSync(filePath, code)

  exec(
    `quirk run temp.qk`,
    { timeout: 5000, cwd: projectRoot },
    (err, stdout, stderr) => {

      const raw = (stdout + stderr).trim()

      // Debug temporarily
      console.log("RAW OUTPUT:", raw)

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