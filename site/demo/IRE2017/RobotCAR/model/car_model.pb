
;
input/batch_sizePlaceholder*
dtype0*
shape:
6
	step/stepConst*
valueB
 :���*
dtype0
�
queue/FIFOQueueFIFOQueueV2*
component_types
2*
shapes
::*
shared_name *
capacityd*
	container 

queue/dequeue_opQueueDequeueManyV2queue/FIFOQueueinput/batch_size*
component_types
2*

timeout_ms���������
�
neural_network_model/Variable_1Const*�
value�B�"�٪����=y��?�&'����+�?]��8́$�C�պ��9�V����r=��#=�T0?^�E���c?����8_��lb�}ՙ�ܽ�|?gڡ�kx>´^������$@y��:W�<��?�1�?�9?<�=*
dtype0
�
$neural_network_model/Variable_1/readIdentityneural_network_model/Variable_1*
T0*2
_class(
&$loc:@neural_network_model/Variable_1
x
neural_network_model/Variable_3Const*A
value8B6",	�XA�{��
���E=ǫ��۰�j'dAB�5AJ�@���Z?�mcA*
dtype0
�
$neural_network_model/Variable_3/readIdentityneural_network_model/Variable_3*
T0*2
_class(
&$loc:@neural_network_model/Variable_3
�
neural_network_model/Variable_5Const*�
value�B�"���Ⱦ����p�3A�G�������?�P�Aw�*�"���U�?���>P-�)�ʽ� ��N{�����<,��,��`:�>9��?*�3@�ӿ�ӿ`|h@j*B<8��Ɖ��3��q&�@��	����qk�(=�?�|@�:俟��b+��M����@�J�>��>��A�?"Z�*�@*
dtype0
�
$neural_network_model/Variable_5/readIdentityneural_network_model/Variable_5*
T0*2
_class(
&$loc:@neural_network_model/Variable_5
\
neural_network_model/Variable_7Const*%
valueB"&n�@�qA�w���&A*
dtype0
�
$neural_network_model/Variable_7/readIdentityneural_network_model/Variable_7*
T0*2
_class(
&$loc:@neural_network_model/Variable_7
�
neural_network_model/MatMulMatMulqueue/dequeue_op$neural_network_model/Variable_1/read*
T0*
transpose_a( *
transpose_b( 
k
neural_network_model/AddAddneural_network_model/MatMul$neural_network_model/Variable_3/read*
T0
D
neural_network_model/ReluReluneural_network_model/Add*
T0
�
neural_network_model/MatMul_1MatMulneural_network_model/Relu$neural_network_model/Variable_5/read*
transpose_a( *
transpose_b( *
T0
r
neural_network_model/output_yAddneural_network_model/MatMul_1$neural_network_model/Variable_7/read*
T0
M
neural_network_model/scoreSoftmaxneural_network_model/output_y*
T0
C
accuracy/ArgMax/dimensionConst*
value	B :*
dtype0
{
accuracy/ArgMaxArgMaxneural_network_model/output_yaccuracy/ArgMax/dimension*
T0*
output_type0	*

Tidx0
E
accuracy/ArgMax_1/dimensionConst*
dtype0*
value	B :
t
accuracy/ArgMax_1ArgMaxqueue/dequeue_op:1accuracy/ArgMax_1/dimension*

Tidx0*
T0*
output_type0	
D
accuracy/EqualEqualaccuracy/ArgMaxaccuracy/ArgMax_1*
T0	
=
accuracy/CastCastaccuracy/Equal*

SrcT0
*

DstT0
<
accuracy/ConstConst*
valueB: *
dtype0
^
accuracy/accuracyMeanaccuracy/Castaccuracy/Const*
T0*

Tidx0*
	keep_dims(  