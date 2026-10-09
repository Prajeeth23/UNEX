using System;
using System.IO;
using System.Diagnostics;
using System.Windows.Forms;

namespace UNEXLauncher
{
    static class Program
    {
        [STAThread]
        static void Main()
        {
            string baseDir = AppDomain.CurrentDomain.BaseDirectory;
            string projectDir = baseDir;

            if (!File.Exists(Path.Combine(projectDir, "start_unex.py")))
            {
                string subDir = Path.Combine(baseDir, "UNEX");
                if (File.Exists(Path.Combine(subDir, "start_unex.py")))
                {
                    projectDir = subDir;
                }
            }

            if (!File.Exists(Path.Combine(projectDir, "start_unex.py")))
            {
                MessageBox.Show(
                    "Could not find 'start_unex.py'. Please make sure UNEX.exe is inside the UNEX directory.",
                    "UNEX OS - Launcher Error",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error
                );
                return;
            }

            string pythonExe = Path.Combine(projectDir, ".venv", "Scripts", "python.exe");
            if (!File.Exists(pythonExe))
            {
                pythonExe = Path.Combine(projectDir, "venv", "Scripts", "python.exe");
            }
            if (!File.Exists(pythonExe))
            {
                pythonExe = "python.exe";
            }

            ProcessStartInfo psi = new ProcessStartInfo
            {
                FileName = pythonExe,
                Arguments = "start_unex.py",
                WorkingDirectory = projectDir,
                UseShellExecute = false,
                CreateNoWindow = true,
                WindowStyle = ProcessWindowStyle.Hidden
            };

            psi.EnvironmentVariables["PYTHONIOENCODING"] = "utf-8";
            psi.EnvironmentVariables["PYTHONUTF8"] = "1";

            try
            {
                Process.Start(psi);
            }
            catch (Exception ex)
            {
                MessageBox.Show(
                    "Failed to start UNEX OS:\n" + ex.Message,
                    "UNEX OS - Launch Failure",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error
                );
            }
        }
    }
}
