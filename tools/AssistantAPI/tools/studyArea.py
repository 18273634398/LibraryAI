# ===========================================================================================================
# Author    ：LuShangWu
# Date      ：2025-01-15
# Version   ：1.0
# Description：用于从服务器获取图书馆自习室数据，并提供预约、签退功能
# Copyright  ：LuShangWu
# License   ：MIT
# Remark   :无
# ===========================================================================================================

from tools.MySQL import cmd

# 获取图书自习室信息
def getStudyArea():
    result = cmd.sqlcmd("select * from study_area")
    return "图书自习室数据解释：AreaName(图书自习室名称),currentNum(当前人数),maxNum(可容纳人数),isOpen(当前是否开放,0为关闭,1为开放),openTime(开放时间)，isOpen的值为0则表示当前该自习室因自身原因不对外开放"+str(result)

# 预约图书自习室
def reserve(name, num):
    try:
        update_sql = f"""
UPDATE study_area
SET currentNum = currentNum + {num}
WHERE AreaName = '{name}' AND currentNum + {num} <= sumNum AND isOpen = 1;
        """
        conn = cmd.connectToMySQL()
        cursor = conn.cursor()
        # 执行SQL语句
        cursor.execute(update_sql)
        # 提交事务
        conn.commit()
        affected_rows = cursor.rowcount
        # 关闭游标和连接
        cursor.close()
        conn.close()
        if affected_rows > 0:
            return f"【预约成功】自习室({name})预约成功，预约人数{num}人"
        else:
            return f"【预约失败】自习室({name})预约失败，可能是因为已经达到最大容量或自习室未开放"
    except Exception as e:
        print(e)
        return "【预约失败】请检查输入是否正确"

# 签退自习室
def signout(name, num):
    try:
        update_sql = f"""
UPDATE study_area
SET currentNum = currentNum - {num}
WHERE AreaName = '{name}' AND currentNum - {num} >= 0 AND isOpen = 1;
        """
        conn = cmd.connectToMySQL()
        cursor = conn.cursor()
        # 执行SQL语句
        cursor.execute(update_sql)
        # 提交事务
        conn.commit()
        affected_rows = cursor.rowcount
        # 关闭游标和连接
        cursor.close()
        conn.close()
        if affected_rows > 0:
            return f"【签退成功】自习室({name})签退成功，签退人数{num}人"
        else:
            return f"【签退失败】自习室({name})签退失败，可能是因为输入的人数大于当前预约人数或自习室未开放"
    except Exception as e:
        print(e)
        return "【签退失败】请检查输入是否正确"



if __name__ == '__main__':
    print(reserve("萃雅书院",120))

