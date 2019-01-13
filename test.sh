filename=$1
txt_file=$2
# txt_file=$(echo "$filename" | sed -r "s/pdf\/(.*)-1\.png/text\/\1.txt/g")
csv_file=$(echo "$filename" | sed -r "s/\.png$/.csv/g")
python3 preprocessing.py --image $filename
echo "Done preprocessing"
julia Lenet.jl $csv_file | tee out_text
python3 text_similarity.py --text $txt_file
