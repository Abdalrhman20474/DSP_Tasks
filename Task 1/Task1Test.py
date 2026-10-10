#!/usr/bin/env python
# coding: utf-8

# In[ ]:


def ReadSignalFile(file_name):
    expected_indices=[]
    expected_samples=[]
    with open(file_name, 'r') as f:
        line = f.readline()
        line = f.readline()
        line = f.readline()
        line = f.readline()
        while line:
            # process line
            L=line.strip()
            if len(L.split(' '))==2:
                L=line.split(' ')
                V1=int(L[0])
                V2=float(L[1])
                expected_indices.append(V1)
                expected_samples.append(V2)
                line = f.readline()
            else:
                break
    return expected_indices,expected_samples


# In[ ]:


def AddSignalSamplesAreEqual(userFirstSignal,userSecondSignal,Your_indices,Your_samples):
    if(userFirstSignal=='Signal1.txt' and userSecondSignal=='Signal2.txt'):
        file_name="output/Signal1+signal2.txt" # write here path of signal1+signal2
    elif(userFirstSignal=='Signal1.txt' and (userSecondSignal=='Signal3.txt' or userSecondSignal=='signal3.txt')):
        file_name="output/signal1+signal3.txt" # write here path of signal1+signal3
    expected_indices,expected_samples=ReadSignalFile(file_name)          
    if (len(expected_samples)!=len(Your_samples)) and (len(expected_indices)!=len(Your_indices)):
        print("Addition Test case failed, your signal have different length from the expected one")
        return
    for i in range(len(Your_indices)):
        if(Your_indices[i]!=expected_indices[i]):
            print("Addition Test case failed, your signal have different indicies from the expected one") 
            return
    for i in range(len(expected_samples)):
        if abs(Your_samples[i] - expected_samples[i]) < 0.01:
            continue
        else:
            print("Addition Test case failed, your signal have different values from the expected one") 
            return
    print("Addition Test case passed successfully")


# In[ ]:


def MultiplySignalByConst(User_Const,Your_indices,Your_samples):
    if(User_Const==5):
        file_name="output/MultiplySignalByConstant-Signal1 - by 5.txt" # write here path of MultiplySignalByConstant-Signal1 - by 5.txt
    elif(User_Const==10):
        file_name="output/MultiplySignalByConstant-signal2 - by 10.txt" # write here path of MultiplySignalByConstant-Signal2 - by 10.txt
        
    expected_indices,expected_samples=ReadSignalFile(file_name)      
    if (len(expected_samples)!=len(Your_samples)) and (len(expected_indices)!=len(Your_indices)):
        print("Multiply by "+str(User_Const)+ " Test case failed, your signal have different length from the expected one")
        return
    for i in range(len(Your_indices)):
        if(Your_indices[i]!=expected_indices[i]):
            print("Multiply by "+str(User_Const)+" Test case failed, your signal have different indicies from the expected one") 
            return
    for i in range(len(expected_samples)):
        if abs(Your_samples[i] - expected_samples[i]) < 0.01:
            continue
        else:
            print("Multiply by "+str(User_Const)+" Test case failed, your signal have different values from the expected one") 
            return
    print("Multiply by "+str(User_Const)+" Test case passed successfully")


# In[ ]:


#TaskName => choose it (string explain the name of task like (adding sig1+sig2,subtracting, .... etc.))
#output_file_name => output file path (output file given by TAs)
# Your_indices => your indices list from your code (generated/calculated by you)
# Your_samples => your samples list from your code (generated/calculated by you)
def SignalSamplesAreEqual(TaskName,output_file_name,Your_indices,Your_samples):
    expected_indices=[]
    expected_samples=[]
    with open(output_file_name, 'r') as f:
        line = f.readline()
        line = f.readline()
        line = f.readline()
        line = f.readline()
        while line:
            # process line
            L=line.strip()
            if len(L.split(' '))==2:
                L=line.split(' ')
                V1=int(L[0])
                V2=float(L[1])
                expected_indices.append(V1)
                expected_samples.append(V2)
                line = f.readline()
            else:
                break
    if (len(expected_samples)!=len(Your_samples)) and (len(expected_indices)!=len(Your_indices)):
         print(TaskName+" Test case failed, your signal have different length from the expected one")
         return
    for i in range(len(Your_indices)):
        if(Your_indices[i]!=expected_indices[i]):
            print(TaskName+" Test case failed, your signal have different indicies from the expected one") 
            return             
    for i in range(len(expected_samples)):
        if abs(Your_samples[i] - expected_samples[i]) < 0.01:
            continue
        else:
            print(TaskName+" Test case failed, your signal have different values from the expected one") 
            return
    print(TaskName+" Test case passed successfully")


def main():
    import os
    import sys

    base_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(base_dir)
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)
    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)
    os.chdir(base_dir)

    from file_io import read_signal
    from operations import add_signals, multiply_signal

    in_dir = os.path.join(base_dir, "input")
    s1 = read_signal(os.path.join(in_dir, "Signal1.txt"))
    s2 = read_signal(os.path.join(in_dir, "Signal2.txt"))
    s3 = read_signal(os.path.join(in_dir, "signal3.txt"))

    print("--- Testing Addition ---")
    sum12 = add_signals([s1, s2])
    AddSignalSamplesAreEqual('Signal1.txt', 'Signal2.txt', sum12.indices, sum12.amplitudes)

    sum13 = add_signals([s1, s3])
    AddSignalSamplesAreEqual('Signal1.txt', 'signal3.txt', sum13.indices, sum13.amplitudes)

    print("\n--- Testing Multiplication ---")
    mul1 = multiply_signal(s1, 5)
    MultiplySignalByConst(5, mul1.indices, mul1.amplitudes)

    mul2 = multiply_signal(s2, 10)
    MultiplySignalByConst(10, mul2.indices, mul2.amplitudes)


if __name__ == "__main__":
    main()

