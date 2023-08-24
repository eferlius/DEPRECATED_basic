import pandas as pd
import datetime

def convert_timestring_to_seconds(string, fmt = '%M:%S.%f'):
    pt = datetime.datetime.strptime(string, fmt)
    return pt.microsecond/10**6 + pt.second + pt.minute*60 + pt.hour*3600
    

def df_convert_timestring_to_seconds(df, time_cols, fmt = '%M:%S.%f'):
    '''
    Converts all the columns of df listed in time_cols from the format 
    declared with fmt to seconds.microseconds

    Parameters
    ----------
    df : pandas df
        pandas dataframe whose columns needs to be converted.
    time_cols : list of strings
        name of the columns whose values needs to be converted from timestring to seconds.
    fmt : string, optional
        format of conversion from timestring to seconds. The default is '%M:%S.%f'.

    Returns
    -------
    df : pandas df
        same as input but with time_cols modified.

    '''
    for col in list(df):
        if col in time_cols:
            for i in df.index:
                df.loc[i,col] = convert_timestring_to_seconds(df.loc[i,col],fmt) 
    return df


def from_TIMES_to_ACTION01_for_each_time(time_df, actions_df, time_col = 'time', 
                                         actions_col = 'action', start_time_col = 'start_time', 
                                         end_time_col = 'end_time'):
    '''
    Given two dataframes:
        time_df, contains a column with all the time values, as declare in time_col
        actions_df, contains 3 columns: 
            action: the name of the action of each row, as declared in actions_col 
            start_time: the start time of each row, as declared in start_time_col
            end_time: the end time of each row, as declared in end_time_col
            
    creates a new dataframe with the time_col from time_df and a column for each action.
    for every row, each action can be 0 or 1.
    0: there is no row in action_df in which the time corresponding to that row 
    is between a start_time and an end_time of that action
    1: there is at least one row in action_df in which the time corresponding to that row 
    is between a start_time and an end_time of that action

    Parameters
    ----------
    time_df : pandas df
        contains the column with all the time instants
    actions_df : pandas df
        three columns "action", "start_time", "end_time"
    timestamp_col : string, optional
        name of the column in time_df where getting the time values. The default is 'time'.
    actions_col : TYPE, optional
        name of the column in actions_df the action names. The default is 'action'.
    start_time_col : TYPE, optional
        name of the column in actions_df the start time values. The default is 'start_time'.
    end_time_col : TYPE, optional
        name of the column in actions_df the end time values. The default is 'end_time'.

    Returns
    -------
    df : pandas df
        DESCRIPTION.

    '''
    # creates a new df with only the time values
    df = pd.DataFrame({time_col:time_df[time_col].values})
    # for every action, creates a column with only 0s 
    for action in actions_df[actions_col].unique():
        df[action] = 0
    # for each row of actions_df, get action start and end time
    for i in actions_df.index:
        action = actions_df[actions_col][i]
        start_time_seconds = actions_df[start_time_col][i]
        end_time_seconds = actions_df[end_time_col][i]
        # for each element of the column time, check if it is between start and end time. 
        # if yes, make it 1 and not 0
        for j in df.index:
            if df[time_col][j] >= start_time_seconds and df[time_col][j] <= end_time_seconds:
                df.loc[j,action] = 1   
    return df