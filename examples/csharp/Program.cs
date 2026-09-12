using System;
using MystiLink.Horoscope;

class Program
{
    static int Main()
    {
        try
        {
            Console.WriteLine(HoroscopeCli.Version());
            Console.WriteLine(HoroscopeCli.Natal(
                "1990-06-15 14:30",
                "Asia/Shanghai",
                31.2304,
                121.4737));
            return 0;
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine(ex.Message);
            return 1;
        }
    }
}
