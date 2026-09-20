using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Text;

namespace Mystilink.Horoscope;

/// <summary>
/// Spawns mystilink-horoscope (or MYSTILINK_HOROSCOPE_CLI) and returns JSON stdout.
/// </summary>
public static class HoroscopeCli
{
    public static string ResolveCli()
    {
        var env = Environment.GetEnvironmentVariable("MYSTILINK_HOROSCOPE_CLI");
        return string.IsNullOrWhiteSpace(env) ? "horoscope" : env;
    }

    public static string Run(params string[] args)
    {
        var psi = new ProcessStartInfo
        {
            FileName = ResolveCli(),
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
            CreateNoWindow = true,
            StandardOutputEncoding = Encoding.UTF8,
            StandardErrorEncoding = Encoding.UTF8,
        };
        foreach (var a in args)
        {
            psi.ArgumentList.Add(a);
        }

        using var proc = Process.Start(psi)
            ?? throw new InvalidOperationException("Failed to start CLI process.");
        var stdout = proc.StandardOutput.ReadToEnd();
        var stderr = proc.StandardError.ReadToEnd();
        proc.WaitForExit();
        if (proc.ExitCode != 0)
        {
            throw new InvalidOperationException(
                string.IsNullOrWhiteSpace(stderr) ? stdout : stderr);
        }
        return stdout;
    }

    public static string Version() => Run("version");

    public static string Natal(
        string datetime,
        string timezone,
        double lat,
        double lon,
        string houseSystem = "P",
        string zodiac = "tropical",
        bool trueSolarTime = false,
        bool noAspects = false)
    {
        var args = new List<string>
        {
            "natal",
            "--datetime", datetime,
            "--timezone", timezone,
            "--lat", lat.ToString(System.Globalization.CultureInfo.InvariantCulture),
            "--lon", lon.ToString(System.Globalization.CultureInfo.InvariantCulture),
            "--house-system", houseSystem,
            "--zodiac", zodiac,
        };
        if (trueSolarTime) args.Add("--true-solar-time");
        if (noAspects) args.Add("--no-aspects");
        return Run(args.ToArray());
    }
}
