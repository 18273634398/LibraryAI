from tools.MySQL import cmd
def getLibraryOperationReport():
    # 返回图书馆运行报告
    try:
        result = cmd.sqlcmd("SELECT * FROM library_operations")
        return f"【图书馆运行日志】{result}\n【任务】请根据日志分析图书馆运行情况，并提出改进建议。尤其是当图书馆运行中有异常情况出现时"
    except Exception as e:
        return f"【图书馆运行日志】获取失败，请检查数据库连接或日志文件是否存在。\n【错误原因】{e}"

