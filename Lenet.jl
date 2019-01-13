using Knet
using Images
using CSV
using Random
using JLD2

Knet.seed!(42)

rev_label_list = Dict(1=> "0", 2=> "1", 3=> "2", 4=> "3", 5=> "4", 6=> "5", 7=> "6", 8=> "7", 9=> "8", 10=> "9", 11=> "A", 12=> "B", 13=> "C", 14=> "D", 15=> "E", 16=> "F", 17=> "G", 18=> "H", 19=> "I", 20=> "J", 21=> "K", 22=> "L", 23=> "M", 24=> "N", 25=> "O", 26=> "P", 27=> "Q", 28=> "R", 29=> "S", 30=> "T", 31=> "U", 32=> "V", 33=> "W", 34=> "X", 35=> "Y", 36=> "Z", 37=> "a", 38=> "b", 39=> "c", 40=> "d", 41=> "e", 42=> "f", 43=> "g", 44=> "h", 45=> "i", 46=> "j", 47=> "k", 48=> "l", 49=> "m", 50=> "n", 51=> "o", 52=> "p", 53=> "q", 54=> "r", 55=> "s", 56=> "t", 57=> "u", 58=> "v", 59=> "w", 60=> "x", 61=> "y", 62=> "z")

# s = ArgParseSettings()
# @add_arg_table s begin
#     ("--df";arg_type=String ; help="Input chars file")
#     ("--train";action = :store_true ;default=false ;help="Training or prediction")
# end
# opts = parse_args(s;as_symbols=true)

train = false

ftype = gpu() >= 0 ? KnetArray{Float32} : Array{Float32}

# LeNet model
function predict(w,x)
    n=length(w)-4
    for i=1:2:n
        x = pool(relu.(conv4(w[i],x) .+ w[i+1]))
    end
    for i=n+1:2:length(w)-2
        x = relu.(w[i]*mat(x) .+ w[i+1])
    end
    return w[end-1]*x .+ w[end]
end

if train

    @load "char_data2.jld2" xtrn ytrn1 xtst ytst1

    dtst = minibatch(xtst,ytst1,64;xtype=ftype)
    dtrn = minibatch(xtrn,ytrn1,64;xtype=ftype)

    loss(w,x,ygold) = nll(predict(w,x),ygold)

    lossgradient = gradloss(loss)


    wcnn=map(ftype, [ xavier(5,5,1,20),  zeros(1,1,20,1), 
                      xavier(5,5,20,50), zeros(1,1,50,1),
                      xavier(500,800),  zeros(500,1),
                      xavier(62,500),  zeros(62,1) ])

    optim = optimizers(wcnn, Adam)

    # training loop
    function train!(w, data, optim)
        lvals = []
        for (x,y) in data
            dw,lval = lossgradient(w, x, y)
            push!(lvals,lval)
            update!(w, dw, optim)
        end
        avg_loss = Knet.mean(lvals)
        return avg_loss
    end

    for epoch in 1:40
        lval = train!(wcnn, dtrn, optim)
        println("Epoch : ", epoch, " Loss : ", lval)
    end

    accs = []
    for (x1,y1) in dtst
        push!(accs,accuracy(predict(wcnn,x1),y1))
    end
    println(Knet.mean(accs))

    wcnn = map(Array{Float32}, wcnn)
    # @save "model.jld2" wcnn

else

    @load "model.jld2" wcnn

    wcnn = map(ftype, wcnn)

    df = CSV.read(ARGS[1])

    df[:,3] = Vector{Array{Float32}}(undef, size(df,1))

    for i in 1:size(df,1)
        if df[i,2] == 0.0
            df[i,3] = Array{Float32}(reshape(eval(Meta.parse(df[i,1])), (28,28,1)))
        end
    end

    x = reshape(Array{Float32}(undef, 28*28*size(df,1)), (28,28,1,size(df,1)))

    for i in 1:size(df,1)
        if df[i,2] == 0.0
            x[:,:,:,i] = df[i,3]
        end
    end

    text = ""
    for i in 1:size(df,1)
        global text
        if df[i,2] == 0.0
            cls = findmax(Array{Float32}(predict(wcnn,ftype(reshape(x[:,:,:,i], (28,28,1,1))))))
            text = string(text, rev_label_list[cls[2][1]])
        else
            text = string(text, " ")
        end
    end

    println(text)

end
